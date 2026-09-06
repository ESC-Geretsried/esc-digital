<?php
/**
 * Plugin Name: ESC Spieler des Spiels
 * Description: Redakteursgesteuerte 18-Minuten-Abstimmung für River-Rats-Heimspiele.
 * Version: 0.2.4
 */
if (!defined('ABSPATH')) exit;

final class ESC_Player_Voting {
    const CPT = 'esc_player_voting';
    const CRON = 'esc_player_voting_expiry';

    public static function boot() {
        add_shortcode('esc_player_voting_prepare', [__CLASS__, 'prepare_shortcode']);
        add_shortcode('esc_player_voting', [__CLASS__, 'public_shortcode']);
        add_action('rest_api_init', [__CLASS__, 'routes']);
        add_action(self::CRON, [__CLASS__, 'expire'], 10, 1);
        add_action('wp_enqueue_scripts', [__CLASS__, 'assets']);
        add_action('admin_enqueue_scripts', [__CLASS__, 'assets']);
        add_action('template_redirect', [__CLASS__, 'frontend_prepare_editor'], 1);
    }

    public static function activate() {
        global $wpdb;
        $table = $wpdb->prefix . 'esc_player_votings';
        $charset = $wpdb->get_charset_collate();
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta("CREATE TABLE $table (id bigint unsigned NOT NULL AUTO_INCREMENT, season varchar(20) NOT NULL, game_key varchar(80) NOT NULL, home_team varchar(120) NOT NULL, away_team varchar(120) NOT NULL, start_at datetime NOT NULL, ends_at datetime NOT NULL, home_players longtext NOT NULL, away_players longtext NOT NULL, status varchar(20) NOT NULL DEFAULT 'active', news_post_id bigint unsigned NOT NULL DEFAULT 0, created_by bigint unsigned NOT NULL DEFAULT 0, created_at datetime NOT NULL, PRIMARY KEY (id), KEY game_key (game_key), KEY status_ends (status,ends_at)) $charset;");
        dbDelta("CREATE TABLE {$wpdb->prefix}esc_player_votes (id bigint unsigned NOT NULL AUTO_INCREMENT, voting_id bigint unsigned NOT NULL, player_key varchar(120) NOT NULL, created_at datetime NOT NULL, PRIMARY KEY (id), KEY voting_player (voting_id,player_key)) $charset;");
        self::page('Spielervoting vorbereiten', 'spielervotingvorbereiten', '[esc_player_voting_prepare]');
        self::page('Spieler des Spiels', 'spielerdesspiels', '[esc_player_voting]');
    }

    private static function page($title, $slug, $content) {
        if (!get_page_by_path($slug)) wp_insert_post(['post_title'=>$title,'post_name'=>$slug,'post_content'=>$content,'post_status'=>'publish','post_type'=>'page']);
    }

    public static function assets() {
        $admin_page = is_admin() && isset($_GET['page']) && $_GET['page'] === 'esc-player-voting';
        if (!$admin_page && !is_page(['spielervotingvorbereiten','spielerdesspiels'])) return;
        wp_register_style('esc-player-voting', false); wp_enqueue_style('esc-player-voting');
        wp_add_inline_style('esc-player-voting', self::css());
        wp_register_script('esc-player-voting', false, [], false, true); wp_enqueue_script('esc-player-voting');
        wp_add_inline_script('esc-player-voting', self::js());
        wp_add_inline_script('esc-player-voting', self::admin_js());
        wp_add_inline_script('esc-player-voting', self::next_game_js());
        wp_add_inline_style('esc-player-voting', self::next_game_css());
        wp_add_inline_style('esc-player-voting', self::next_game_css_override());
        wp_localize_script('esc-player-voting','ESC_VOTING',['root'=>esc_url_raw(rest_url('esc/v1/')),'nonce'=>wp_create_nonce('wp_rest')]);
    }

    public static function frontend_prepare_editor() {
        $path = trim((string) parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH), '/');
        if ($path !== 'spielervotingvorbereiten') return;
        if (!is_user_logged_in()) { auth_redirect(); exit; }
        if (!current_user_can('edit_posts')) wp_die('Für das Spielervoting besteht keine Berechtigung.');
        status_header(200);
        add_filter('pre_get_document_title', function() { return 'Spielervoting vorbereiten · ESC River Rats Geretsried e.V.'; });
        get_header();
        echo '<main class="section shell esc-vote-frontend">' . do_shortcode('[esc_player_voting_prepare]') . '</main>';
        get_footer();
        exit;
    }

    public static function prepare_shortcode() {
        if (!is_user_logged_in() || !current_user_can('edit_posts')) return '<div class="esc-vote-gate">Dieser Bereich ist nur für berechtigte Redakteure sichtbar.</div>';
        ob_start(); ?>
        <div class="esc-vote-admin esc-vote-wrap"><div class="esc-vote-kicker">REDaktion · River Rats</div><h1>Spielervoting vorbereiten</h1><p class="esc-vote-lead">Drei Heim- und drei Gastspieler eintragen. Mit „Voting starten“ beginnt die Abstimmung für exakt 18 Minuten.</p>
        <form id="esc-vote-prepare"><div class="esc-vote-grid"><label>Saison*<input name="season" value="2026/2027" required></label><label>Spielbeginn*<input name="start_at" type="datetime-local" required></label><label>Heimmannschaft*<input name="home_team" value="ESC River Rats Geretsried" required></label><label>Gastmannschaft*<input name="away_team" required></label></div><div class="esc-vote-columns"><fieldset><legend>Heim · drei Spieler</legend><?php for($i=1;$i<=3;$i++): ?><label>Spieler <?php echo $i; ?><input name="home_players[]" required maxlength="80"></label><?php endfor; ?></fieldset><fieldset><legend>Gast · drei Spieler</legend><?php for($i=1;$i<=3;$i++): ?><label>Spieler <?php echo $i; ?><input name="away_players[]" required maxlength="80"></label><?php endfor; ?></fieldset></div><p id="esc-vote-admin-status" class="esc-vote-status"></p><button class="esc-vote-button" type="submit">Voting starten · 18 Minuten</button></form><div class="esc-vote-stop"><h2>Aktives Voting</h2><p id="esc-vote-active-admin">Kein Voting aktiv.</p><button id="esc-vote-stop" class="esc-vote-danger" type="button" hidden>Voting jetzt beenden</button></div><div class="esc-vote-reset"><h2>Saison zurücksetzen</h2><p>Löscht die Voting-Historie dieser Saison und die automatisch erstellten Voting-News. Diese Aktion ist nicht rückgängig zu machen.</p><button id="esc-vote-reset" class="esc-vote-danger" type="button">Saison zurücksetzen</button></div></div><?php return ob_get_clean();
    }

    public static function public_shortcode() {
        ob_start(); ?><div class="esc-vote-public esc-vote-wrap"><div class="esc-vote-kicker">LIVE · Nur River-Rats-Heimspiele</div><h1>Spieler des Spiels</h1><p class="esc-vote-lead">Stimme im letzten Drittel für deinen Spieler des Spiels. Die Abstimmung läuft 18 Minuten.</p><div id="esc-vote-live"><div class="esc-vote-loading">Nächstes Heimspiel wird geladen …</div></div><section class="esc-vote-history"><div class="esc-vote-kicker">Historie</div><h2>Spieler des Spiels</h2><div id="esc-vote-history-list"></div></section></div><?php return ob_get_clean();
    }

    public static function routes() {
        register_rest_route('esc/v1','/voting/current',['methods'=>'GET','callback'=>[__CLASS__,'current'],'permission_callback'=>'__return_true']);
        register_rest_route('esc/v1','/voting/start',['methods'=>'POST','callback'=>[__CLASS__,'start'],'permission_callback'=>function(){return current_user_can('edit_posts');}]);
        register_rest_route('esc/v1','/voting/stop',['methods'=>'POST','callback'=>[__CLASS__,'stop'],'permission_callback'=>function(){return current_user_can('edit_posts');}]);
        register_rest_route('esc/v1','/voting/(?P<id>\d+)/vote',['methods'=>'POST','callback'=>[__CLASS__,'vote'],'permission_callback'=>'__return_true']);
        register_rest_route('esc/v1','/voting/reset',['methods'=>'POST','callback'=>[__CLASS__,'reset'],'permission_callback'=>function(){return current_user_can('manage_options');}]);
    }

    private static function table() { global $wpdb; return $wpdb->prefix.'esc_player_votings'; }
    private static function row($id) { global $wpdb; return $wpdb->get_row($wpdb->prepare('SELECT * FROM '.self::table().' WHERE id=%d',$id)); }
    private static function json($value) { return array_values(array_filter(array_map('sanitize_text_field',(array)$value))); }

    public static function start(WP_REST_Request $req) {
        global $wpdb; $p=$req->get_json_params(); $home=sanitize_text_field($p['home_team']??'');
        if (stripos($home,'river rats')===false || count(self::json($p['home_players']??[]))!==3 || count(self::json($p['away_players']??[]))!==3) return new WP_Error('invalid','Nur Heimspiele der River Rats mit exakt drei Spielern je Team sind zulässig.', ['status'=>400]);
        $start=sanitize_text_field($p['start_at']??''); $ts=strtotime($start); if(!$ts) return new WP_Error('invalid','Spielbeginn fehlt.', ['status'=>400]);
        $end=$ts+18*60; $key=wp_generate_uuid4(); $wpdb->insert(self::table(),['season'=>sanitize_text_field($p['season']??'2026/2027'),'game_key'=>$key,'home_team'=>$home,'away_team'=>sanitize_text_field($p['away_team']??''),'start_at'=>gmdate('Y-m-d H:i:s',$ts),'ends_at'=>gmdate('Y-m-d H:i:s',$end),'home_players'=>wp_json_encode(self::json($p['home_players'])),'away_players'=>wp_json_encode(self::json($p['away_players'])),'status'=>'active','created_by'=>get_current_user_id(),'created_at'=>current_time('mysql',true)]);
        $id=(int)$wpdb->insert_id; wp_schedule_single_event($end,self::CRON,[$id]); return ['id'=>$id,'ends_at'=>gmdate(DATE_ATOM,$end),'message'=>'Voting gestartet.'];
    }

    public static function stop(WP_REST_Request $req) {
        $id=(int)($req->get_json_params()['id']??0); $row=self::row($id);
        if(!$row || $row->status!=='active') return new WP_Error('not_active','Kein aktives Voting gefunden.',['status'=>404]);
        global $wpdb; $wpdb->update(self::table(),['ends_at'=>gmdate('Y-m-d H:i:s')],['id'=>$id]); self::expire($id); return ['message'=>'Voting beendet und Ergebnis-News erstellt.'];
    }

    public static function current() { global $wpdb; self::expire(); $row=$wpdb->get_row("SELECT * FROM ".self::table()." WHERE status='active' AND ends_at > UTC_TIMESTAMP() ORDER BY ends_at ASC LIMIT 1"); $history=$wpdb->get_results("SELECT * FROM ".self::table()." WHERE status='finished' ORDER BY ends_at DESC LIMIT 12"); return ['active'=>$row?self::public_row($row):null,'history'=>array_map([__CLASS__,'public_row'],$history)]; }
    private static function public_row($r) { return ['id'=>(int)$r->id,'season'=>$r->season,'home_team'=>$r->home_team,'away_team'=>$r->away_team,'start_at'=>$r->start_at,'ends_at'=>$r->ends_at,'home_players'=>json_decode($r->home_players,true),'away_players'=>json_decode($r->away_players,true),'scores'=>self::scores($r->id),'status'=>$r->status,'news_post_id'=>(int)$r->news_post_id]; }
    private static function scores($id) { global $wpdb; $votes=$wpdb->get_results($wpdb->prepare("SELECT player_key, COUNT(*) n FROM {$wpdb->prefix}esc_player_votes WHERE voting_id=%d GROUP BY player_key",$id)); $out=[]; foreach($votes as $v)$out[$v->player_key]=(int)$v->n; return $out; }

    public static function vote(WP_REST_Request $req) { global $wpdb; $id=(int)$req['id']; $row=self::row($id); if(!$row || $row->status!=='active' || strtotime($row->ends_at)<=time()) return new WP_Error('closed','Die Abstimmung ist beendet.',['status'=>409]); $key=sanitize_text_field($req->get_json_params()['player_key']??''); $allowed=array_merge(json_decode($row->home_players,true),json_decode($row->away_players,true)); if(!in_array($key,$allowed,true)) return new WP_Error('invalid','Ungültiger Spieler.',['status'=>400]); $cookie='esc_voted_'.$id; if(!empty($_COOKIE[$cookie])) return new WP_Error('already_voted','Du hast bereits abgestimmt.',['status'=>409]); $wpdb->insert($wpdb->prefix.'esc_player_votes',['voting_id'=>$id,'player_key'=>$key,'created_at'=>current_time('mysql',true)]); setcookie($cookie,'1',time()+DAY_IN_SECONDS,'/',COOKIEPATH, is_ssl(),true); return ['scores'=>self::scores($id)]; }

    public static function expire($id=0) { global $wpdb; $where=$id?' AND id='.(int)$id:''; $rows=$wpdb->get_results("SELECT * FROM ".self::table()." WHERE status='active' AND ends_at <= UTC_TIMESTAMP() $where"); foreach($rows as $r){$scores=self::scores($r->id);$all=array_merge(json_decode($r->home_players,true),json_decode($r->away_players,true));$winner='Noch keine Stimmen';$max=0;foreach($all as $p){if(($scores[$p]??0)>$max){$max=$scores[$p];$winner=$p;}}$cat=get_category_by_slug('river-rats');$post=wp_insert_post(['post_title'=>'Spieler des Spiels · '.$r->home_team.' vs. '.$r->away_team,'post_content'=>'<p><strong>Spieler des Spiels</strong></p><p>Heim: '.esc_html($winner).' · Stimmen: '.$max.'</p><p>Abstimmung beendet nach 18 Minuten.</p>','post_status'=>'publish','post_type'=>'post','post_category'=>$cat?[$cat->term_id]:[],'meta_input'=>['_esc_player_voting_id'=>$r->id]]);$wpdb->update(self::table(),['status'=>'finished','news_post_id'=>(int)$post],['id'=>$r->id]);}}
    public static function reset(WP_REST_Request $req) { global $wpdb; $season=sanitize_text_field($req->get_json_params()['season']??''); if(!$season)return new WP_Error('invalid','Saison fehlt.',['status'=>400]);$ids=$wpdb->get_col($wpdb->prepare('SELECT id FROM '.self::table().' WHERE season=%s',$season));foreach($ids as $id)wp_clear_scheduled_hook(self::CRON,[$id]);if($ids){$in=implode(',',array_map('intval',$ids));$wpdb->query("DELETE FROM {$wpdb->prefix}esc_player_votes WHERE voting_id IN ($in)");$wpdb->query("DELETE FROM ".self::table()." WHERE id IN ($in)");}return ['deleted'=>count($ids)]; }

    private static function css() { return '.esc-vote-wrap{--navy:#071f38;--gold:#c48714;--ink:#122b46;--pale:#f1f4f6;color:var(--ink);max-width:1120px;margin:0 auto;padding:52px 20px}.esc-vote-wrap h1{font-size:clamp(42px,7vw,84px);line-height:.98;color:var(--navy);margin:10px 0 22px;border-bottom:4px solid var(--gold);padding-bottom:24px}.esc-vote-wrap h2{color:var(--navy);font-size:32px}.esc-vote-kicker{text-transform:uppercase;color:var(--gold);font-weight:800;letter-spacing:.15em}.esc-vote-lead{font-size:21px;line-height:1.5;max-width:760px}.esc-vote-grid,.esc-vote-columns{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin:25px 0}.esc-vote-columns{align-items:start}.esc-vote-wrap fieldset,.esc-vote-wrap label{display:flex;flex-direction:column;gap:7px;font-weight:800}.esc-vote-wrap fieldset{background:var(--pale);border:0;border-top:4px solid var(--gold);padding:22px}.esc-vote-wrap legend{font-size:24px;color:var(--navy);margin-bottom:15px}.esc-vote-wrap input{border:1px solid #ccd6df;background:#fff;padding:13px;font:inherit;color:var(--ink)}.esc-vote-button{background:var(--gold);color:#fff;border:0;padding:16px 22px;font:inherit;font-weight:800;cursor:pointer}.esc-vote-status{min-height:24px;font-weight:800}.esc-vote-danger{border:1px solid #a32323;background:#fff;color:#a32323;padding:12px 18px;font:inherit;font-weight:800}.esc-vote-reset{margin-top:48px;border-top:1px solid #ccd6df;padding-top:22px}.esc-vote-loading,.esc-vote-empty{background:var(--pale);padding:30px;border-top:4px solid var(--gold)}.esc-vote-match{background:var(--navy);color:#fff;padding:28px;border-top:5px solid var(--gold)}.esc-vote-match h2{color:#fff;margin:8px 0}.esc-vote-countdown{font-size:26px;color:var(--gold);font-weight:800}.esc-vote-teams{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:25px}.esc-vote-team{background:#fff;color:var(--ink);padding:18px}.esc-vote-team h3{margin:0 0 12px;color:var(--navy)}.esc-vote-player{display:flex;justify-content:space-between;align-items:center;width:100%;background:#f1f4f6;border:1px solid #ccd6df;padding:12px;margin:8px 0;font:inherit;font-weight:800;color:var(--ink);cursor:pointer}.esc-vote-player:hover,.esc-vote-player.is-selected{background:var(--gold);color:#fff}.esc-vote-bar{height:6px;background:#ccd6df;margin-top:7px}.esc-vote-bar i{display:block;height:100%;background:var(--gold)}.esc-vote-history{margin-top:55px}.esc-vote-history article{border-top:3px solid var(--gold);background:var(--pale);padding:20px;margin:12px 0}.esc-vote-history article strong{color:var(--navy)}@media(max-width:700px){.esc-vote-wrap{padding:30px 14px}.esc-vote-grid,.esc-vote-columns,.esc-vote-teams{grid-template-columns:1fr}.esc-vote-lead{font-size:18px}}'; }
    private static function js() { return "(()=>{const root=window.ESC_VOTING?.root||'/wp-json/esc/v1/';const q=s=>document.querySelector(s);async function get(){const r=await fetch(root+'voting/current');return r.json()}function esc(s){return String(s||'').replace(/[&<>\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#039;'}[m]))}function render(d){const live=q('#esc-vote-live'),hist=q('#esc-vote-history-list');if(live){if(!d.active){live.innerHTML='<div class=\"esc-vote-empty\"><strong>Derzeit ist kein Voting aktiv.</strong><p>Das nächste River-Rats-Heimspiel erscheint hier, sobald das Voting im letzten Drittel gestartet wurde.</p></div>'}else{const v=d.active;const players=[...v.home_players,...v.away_players];const total=Object.values(v.scores||{}).reduce((a,b)=>a+b,0);live.innerHTML='<div class=\"esc-vote-match\"><div class=\"esc-vote-kicker\">LIVE · Abstimmung geöffnet</div><h2>'+esc(v.home_team)+' <span>vs.</span> '+esc(v.away_team)+'</h2><div class=\"esc-vote-countdown\" id=\"esc-vote-clock\"></div><div class=\"esc-vote-teams\"><div class=\"esc-vote-team\"><h3>'+esc(v.home_team)+'</h3>'+v.home_players.map(p=>button(p,v.scores,total,v.id)).join('')+'</div><div class=\"esc-vote-team\"><h3>'+esc(v.away_team)+'</h3>'+v.away_players.map(p=>button(p,v.scores,total,v.id)).join('')+'</div></div><p>Live-Stand · '+total+' Stimme'+(total===1?'':'n')+'</p></div>';tick(v.ends_at)}}if(hist){hist.innerHTML=(d.history||[]).map(v=>{const all=[...v.home_players,...v.away_players],scores=v.scores||{};let win=all[0]||'—';all.forEach(p=>{if((scores[p]||0)>(scores[win]||0))win=p});return '<article><strong>'+esc(v.home_team)+' · '+esc(v.away_team)+'</strong><br>Spieler des Spiels: <b>'+esc(win)+'</b></article>'}).join('')||'<p>Noch keine abgeschlossenen Votings.</p>'}}function button(p,scores,total,id){const n=scores?.[p]||0,pc=total?Math.round(n*100/total):0;return '<button class=\"esc-vote-player\" data-id=\"'+id+'\" data-player=\"'+esc(p)+'\"><span>'+esc(p)+'</span><b>'+n+'</b></button><div class=\"esc-vote-bar\"><i style=\"width:'+pc+'%\"></i></div>'}function tick(end){const el=q('#esc-vote-clock');const f=()=>{const n=Math.max(0,new Date(end).getTime()-Date.now());el.textContent=n?'Ende in '+Math.floor(n/60000)+':'+String(Math.floor(n/1000)%60).padStart(2,'0'):'Voting beendet';if(!n)setTimeout(load,1000)};f();setInterval(f,1000)}async function load(){try{render(await get())}catch(e){}}document.addEventListener('click',async e=>{const b=e.target.closest('.esc-vote-player');if(!b)return;try{const r=await fetch(root+'voting/'+b.dataset.id+'/vote',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({player_key:b.dataset.player})});if(!r.ok){const x=await r.json();alert(x.message||'Stimme nicht möglich');return}load()}catch(_){alert('Stimme konnte nicht übermittelt werden.')}});const f=q('#esc-vote-prepare');if(f)f.addEventListener('submit',async e=>{e.preventDefault();const p=Object.fromEntries(new FormData(f));p.home_players=[...f.querySelectorAll('[name=\"home_players[]\"]')].map(x=>x.value);p.away_players=[...f.querySelectorAll('[name=\"away_players[]\"]')].map(x=>x.value);const r=await fetch(root+'voting/start',{method:'POST',headers:{'Content-Type':'application/json','X-WP-Nonce':window.ESC_VOTING.nonce},body:JSON.stringify(p)});const x=await r.json();q('#esc-vote-admin-status').textContent=x.message||x.code||'Bitte Eingaben prüfen.'});const reset=q('#esc-vote-reset');if(reset)reset.onclick=async()=>{const season=q('[name=\"season\"]')?.value||'2026/2027';if(!confirm('Saison '+season+' wirklich löschen?'))return;if(!confirm('Letzte Sicherheitsabfrage: Alle Voting-Daten und Voting-News dieser Saison endgültig löschen?'))return;const r=await fetch(root+'voting/reset',{method:'POST',headers:{'Content-Type':'application/json','X-WP-Nonce':window.ESC_VOTING.nonce},body:JSON.stringify({season})});alert((await r.json()).deleted+' Datensätze gelöscht.');};load();})();"; }

    private static function admin_js() { return "(()=>{const root=window.ESC_VOTING?.root||'/wp-json/esc/v1/';const q=s=>document.querySelector(s);const stop=q('#esc-vote-stop');async function refresh(){if(!stop)return;const r=await fetch(root+'voting/current'),d=await r.json(),a=q('#esc-vote-active-admin');if(d.active){a.textContent=d.active.home_team+' vs. '+d.active.away_team+' · Abstimmung läuft';stop.hidden=false;stop.dataset.id=d.active.id}else{a.textContent='Kein Voting aktiv.';stop.hidden=true}}if(stop){stop.addEventListener('click',async()=>{if(!confirm('Aktives Voting jetzt beenden und Ergebnis-News erstellen?'))return;const r=await fetch(root+'voting/stop',{method:'POST',headers:{'Content-Type':'application/json','X-WP-Nonce':window.ESC_VOTING.nonce},body:JSON.stringify({id:stop.dataset.id})});const d=await r.json();q('#esc-vote-admin-status').textContent=d.message||d.code;refresh()});refresh();}})();"; }
    private static function next_game_css() { return '.esc-vote-next-game{background:#071f38;color:#fff;border-top:5px solid #c48714;padding:22px 26px;margin:24px 0}.esc-vote-next-game__kicker{color:#c48714;text-transform:uppercase;font-weight:800;letter-spacing:.12em;font-size:13px}.esc-vote-next-game h2{color:#fff;margin:6px 0 8px;font-size:clamp(24px,4vw,42px)}.esc-vote-next-game p{margin:5px 0}.esc-vote-next-game__clock{font-size:clamp(22px,4vw,34px);font-weight:800;color:#fff}.esc-vote-next-game__source{font-size:12px;opacity:.75;margin-top:12px}.esc-vote-suggestion{display:block;color:#596f82;font-size:13px;font-weight:400;margin-top:5px}@media(max-width:700px){.esc-vote-next-game{padding:18px}.esc-vote-next-game h2{font-size:25px}}'; }
    private static function next_game_js() { return <<<'JS'
(()=>{
  const root=document.querySelector('.esc-vote-wrap');
  if(!root)return;
  const esc=s=>String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  const clean=s=>String(s||'').replace(/\s+/g,' ').trim();
  const parseDate=s=>{const m=String(s).match(/(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4})/);return m?new Date(+m[3],+m[2]-1,+m[1]):null};
  const parseTime=s=>{const m=String(s).match(/(\d{1,2}):(\d{2})/);return m?[+m[1],+m[2]]:[0,0]};
  const isHome=s=>/river\s*rats|rrg|geretsried/i.test(s);
  const textOf=cell=>clean(cell?.getAttribute('data-team-name')||cell?.querySelector('[data-team-name]')?.textContent||cell?.querySelector('[title]')?.getAttribute('title')||cell?.querySelector('img')?.getAttribute('alt')||cell?.textContent);
  const imageOf=cell=>cell?.querySelector('img')?.currentSrc||cell?.querySelector('img')?.src||'';
  const displayName=s=>{const key=clean(s).toUpperCase().replace(/[.\s-]/g,'');const known={'KÖN':'EHC Königsbrunn','KON':'EHC Königsbrunn','RRG':'ESC River Rats Geretsried','RIVER RATS':'ESC River Rats Geretsried'};return known[key]||clean(s)};
  const read=doc=>{
    const rows=[...doc.querySelectorAll('.esc-gamepitch-widget table tbody tr, table.esc-gamepitch-widget tbody tr')];
    const games=[];
    rows.forEach(row=>{
      const cells=[...row.querySelectorAll('td')],labels=cells.map(textOf);
      const raw=labels.join(' '), date=parseDate(raw); if(!date)return;
      const tm=parseTime(raw); date.setHours(tm[0],tm[1],0,0);
      if(date<=new Date())return;
      const names=labels.filter(c=>c&& !/\d{1,2}[.\/-]\d{1,2}[.\/-]\d{4}/.test(c) && !/^\d{1,2}:\d{2}$/.test(c) && c.length>2);
      const homeIndex=names.findIndex(isHome); if(homeIndex<0)return;
      const home=displayName(names[homeIndex]),opponent=displayName(names[homeIndex+1]||names[homeIndex-1]||'Nächster Gegner');
      const homeCell=cells.find(c=>textOf(c)===names[homeIndex]),awayCell=cells.find(c=>textOf(c)===(names[homeIndex+1]||names[homeIndex-1]));
      games.push({date,home,opponent,homeLogo:imageOf(homeCell),awayLogo:imageOf(awayCell)});
    });
    return games.sort((a,b)=>a.date-b.date)[0]||null;
  };
  const fmtDate=d=>d.toLocaleDateString('de-DE',{day:'2-digit',month:'2-digit',year:'numeric'});
  const fmtInput=d=>{const z=n=>String(n).padStart(2,'0');return `${d.getFullYear()}-${z(d.getMonth()+1)}-${z(d.getDate())}T${z(d.getHours())}:${z(d.getMinutes())}`};
  const show=game=>{
    if(!game)return;
    const live=document.querySelector('#esc-vote-live');
    if(live && !document.querySelector('.esc-vote-next-game')){
      const box=document.createElement('div');box.className='esc-vote-next-game';
      box.innerHTML=`<div class="esc-vote-next-game__kicker">Nächstes Heimspiel · Hockeydata</div><div class="esc-vote-next-game__teams"><div class="esc-vote-next-game__team"><img src="${esc(game.homeLogo)}" alt="${esc(game.home)}"><strong>${esc(game.home)}</strong></div><div class="esc-vote-next-game__versus">vs.</div><div class="esc-vote-next-game__team"><img src="${esc(game.awayLogo)}" alt="${esc(game.opponent)}"><strong>${esc(game.opponent)}</strong></div></div><p>${fmtDate(game.date)} · ${String(game.date.getHours()).padStart(2,'0')}:${String(game.date.getMinutes()).padStart(2,'0')} Uhr</p><div class="esc-vote-next-game__clock"></div><p class="esc-vote-next-game__source">Das Voting kann im letzten Drittel manuell gestartet werden.</p>`;
      live.prepend(box);
      const clock=box.querySelector('.esc-vote-next-game__clock'); const tick=()=>{const n=Math.max(0,game.date-Date.now());const h=Math.floor(n/36e5),m=Math.floor(n%36e5/6e4),s=Math.floor(n%6e4/1e3);clock.textContent=n?`Start in ${h} Std. ${m} Min. ${s} Sek.`:'Spiel läuft';};tick();setInterval(tick,1000);
    }
    const form=document.querySelector('#esc-vote-prepare'); if(!form)return;
    const away=form.querySelector('[name="away_team"]'), start=form.querySelector('[name="start_at"]');
    if(!form.querySelector('.esc-vote-game-suggestion')){const hint=document.createElement('div');hint.className='esc-vote-game-suggestion';hint.innerHTML=`<div class="esc-vote-game-suggestion__kicker">Spielvorschlag aus Hockeydata</div><div class="esc-vote-game-suggestion__teams"><span><img src="${esc(game.homeLogo)}" alt="">${esc(game.home)}</span><b>vs.</b><span><img src="${esc(game.awayLogo)}" alt="">${esc(game.opponent)}</span></div>`;form.prepend(hint)}
    if(away && !away.value)away.value=game.opponent;
    if(start && !start.value)start.value=fmtInput(game.date);
    [away,start].forEach(field=>{if(!field||field.dataset.escRecovery)return;field.dataset.escRecovery='1';const note=document.createElement('span');note.className='esc-vote-suggestion';note.textContent='Vorschlag aus Hockeydata – bei leerem Feld wird er wieder eingesetzt.';field.parentElement.appendChild(note);let timer;field.addEventListener('input',()=>{clearTimeout(timer);if(!field.value)timer=setTimeout(()=>{field.value=field===away?game.opponent:fmtInput(game.date)},700)});});
  };
  const frame=document.createElement('iframe');frame.setAttribute('aria-hidden','true');frame.tabIndex=-1;frame.style.cssText='position:absolute;width:1px;height:1px;opacity:0;pointer-events:none;border:0';frame.src='/river-rats/';document.body.appendChild(frame);
  frame.addEventListener('load',()=>{let tries=0;const probe=()=>{try{const game=read(frame.contentDocument);if(game){show(game);frame.remove();return}}catch(e){}if(++tries<12)setTimeout(probe,700);else frame.remove()};setTimeout(probe,700)});
})();
JS; }
    private static function next_game_css_override() { return '.esc-vote-next-game h2{color:#fff!important;margin:10px 0 12px;font-size:clamp(28px,4vw,46px);line-height:1.08;font-weight:800;letter-spacing:-.02em}.esc-vote-next-game h2 span{color:#d39a2a;font-size:.72em;margin:0 .12em}.esc-vote-next-game h2 + p{font-size:18px;font-weight:700;color:#fff;margin:0 0 16px}.esc-vote-next-game__teams{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:18px;margin:22px 0 18px}.esc-vote-next-game__team{display:flex;align-items:center;gap:14px;color:#fff;font-size:clamp(18px,2.5vw,28px);line-height:1.15}.esc-vote-next-game__team:last-child{justify-content:flex-end;text-align:right}.esc-vote-next-game__team img{width:64px;height:64px;object-fit:contain;flex:0 0 64px}.esc-vote-next-game__team img[src=""]{display:none}.esc-vote-next-game__versus{color:#d39a2a;font-weight:800;font-size:22px;text-transform:uppercase}.esc-vote-next-game__clock{font-size:clamp(24px,4vw,38px);line-height:1.15;font-weight:800;color:#fff;letter-spacing:-.02em}.esc-vote-next-game:after{content:"";display:block;width:74px;height:4px;background:#d39a2a;margin-top:22px}.esc-vote-game-suggestion{background:#071f38;color:#fff;border-top:4px solid #c48714;padding:18px 22px;margin:0 0 24px}.esc-vote-game-suggestion__kicker{color:#d39a2a;text-transform:uppercase;font-weight:800;letter-spacing:.1em;font-size:13px}.esc-vote-game-suggestion__teams{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:12px;font-size:18px;font-weight:800}.esc-vote-game-suggestion__teams span{display:flex;align-items:center;gap:10px}.esc-vote-game-suggestion__teams img{width:42px;height:42px;object-fit:contain}.esc-vote-game-suggestion__teams img[src=""]{display:none}.esc-vote-game-suggestion__teams b{color:#d39a2a}@media(max-width:700px){.esc-vote-next-game{padding:22px 18px}.esc-vote-next-game__teams{grid-template-columns:1fr auto 1fr;gap:8px}.esc-vote-next-game__team{display:flex;flex-direction:column;gap:7px;text-align:center;font-size:17px}.esc-vote-next-game__team:last-child{justify-content:flex-start;text-align:center}.esc-vote-next-game__team img{width:52px;height:52px;flex-basis:52px}.esc-vote-next-game__versus{font-size:16px}.esc-vote-next-game h2{font-size:28px}.esc-vote-next-game h2 + p{font-size:16px}.esc-vote-next-game__clock{font-size:25px}.esc-vote-game-suggestion{padding:16px}.esc-vote-game-suggestion__teams{font-size:15px}.esc-vote-game-suggestion__teams img{width:36px;height:36px}}'; }
}
ESC_Player_Voting::boot();
register_activation_hook(__FILE__, ['ESC_Player_Voting','activate']);
