<?php
/** ESC River Rats theme bootstrap. */
if ( ! defined( 'ABSPATH' ) ) { exit; }

function esc_river_rats_setup() {
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'responsive-embeds' );
    add_theme_support( 'editor-styles' );
    add_editor_style( 'editor-styles/editor.css' );
}
add_action( 'after_setup_theme', 'esc_river_rats_setup' );

function esc_river_rats_news_categories() {
    return array(
        'verein' => 'Verein', 'river-rats' => 'River Rats', 'nachwuchs' => 'Nachwuchs',
        'damen' => 'Damen', 'eiskunstlauf' => 'Eiskunstlauf', 'inklusion' => 'Inklusion',
        'u7' => 'U7', 'u9' => 'U9', 'u11' => 'U11', 'u13' => 'U13', 'u15' => 'U15', 'u17' => 'U17', 'u20' => 'U20',
        'eislaufschule' => 'Eislaufschule', 'geschaeftsstelle' => 'Geschäftsstelle', 'flashnews' => 'Flashnews',
    );
}

function esc_river_rats_create_news_categories() {
    foreach ( esc_river_rats_news_categories() as $slug => $name ) {
        if ( ! term_exists( $slug, 'category' ) ) { wp_insert_term( $name, 'category', array( 'slug' => $slug ) ); }
    }
}
add_action( 'after_switch_theme', 'esc_river_rats_create_news_categories' );

/* Keep the editor's news choices aligned with the canonical News Tree. */
function esc_river_rats_ensure_news_categories() {
    esc_river_rats_create_news_categories();
    $allowed = array_keys( esc_river_rats_news_categories() );
    $terms = get_terms( array( 'taxonomy' => 'category', 'hide_empty' => false ) );
    if ( is_wp_error( $terms ) ) { return; }
    foreach ( $terms as $term ) {
        if ( 'uncategorized' === $term->slug || in_array( $term->slug, $allowed, true ) ) { continue; }
        if ( 0 === (int) $term->count ) { wp_delete_term( (int) $term->term_id, 'category' ); }
    }
}
add_action( 'init', 'esc_river_rats_ensure_news_categories', 20 );

/* Simplified editorial composer. It creates native posts so all existing
 * archives, filters and category pages continue to work. */
function esc_river_rats_news_editor_areas() {
    return array(
        'river-rats' => 'River Rats', 'damen' => 'Damen', 'u7' => 'U7', 'u9' => 'U9',
        'u11' => 'U11', 'u13' => 'U13', 'u15' => 'U15', 'u17' => 'U17', 'u20' => 'U20',
        'eiskunstlauf' => 'Eiskunstlauf', 'inklusion' => 'Inklusionssport',
        'eislaufschule' => 'Eislaufschule', 'verein' => 'Verein',
        'foerderverein' => 'Förderverein', 'geschaeftsstelle' => 'Geschäftsstelle',
    );
}
function esc_river_rats_news_editor_caps() {
    $caps = array();
    foreach ( array_keys( esc_river_rats_news_editor_areas() ) as $slug ) { $caps[] = 'esc_create_news_' . str_replace( '-', '_', $slug ); }
    return $caps;
}
function esc_river_rats_news_editor_bootstrap_caps() {
    if ( get_option( 'esc_news_editor_caps_initialized' ) ) { return; }
    foreach ( array( 'administrator', 'editor' ) as $role_name ) {
        $role = get_role( $role_name );
        if ( $role ) { foreach ( esc_river_rats_news_editor_caps() as $cap ) { $role->add_cap( $cap ); } }
    }
    update_option( 'esc_news_editor_caps_initialized', 1, false );
}
add_action( 'init', 'esc_river_rats_news_editor_bootstrap_caps', 25 );

function esc_river_rats_news_editor_menu() {
    add_menu_page( 'News erstellen', 'News erstellen', 'edit_posts', 'esc-news-create', 'esc_river_rats_news_editor_page', 'dashicons-edit-page', 7 );
    foreach ( esc_river_rats_news_editor_areas() as $slug => $label ) {
        add_submenu_page( 'esc-news-create', $label . ' – News erstellen', $label, 'esc_create_news_' . str_replace( '-', '_', $slug ), 'esc_river_rats_news_editor_page', null, 10 );
    }
}
add_action( 'admin_menu', 'esc_river_rats_news_editor_menu', 30 );

function esc_river_rats_news_editor_assets( $hook ) {
    if ( false === strpos( $hook, 'esc-news-create' ) ) { return; }
    wp_enqueue_media();
    wp_enqueue_editor();
    wp_add_inline_style( 'common', '.esc-news-create{max-width:980px}.esc-news-create .esc-news-form{max-width:860px;background:#fff;border:1px solid #dcdcde;padding:26px;margin-top:20px}.esc-news-create .esc-news-form label{display:block;margin-bottom:7px}.esc-news-create .esc-media-preview{min-height:20px;margin-top:10px}.esc-news-create .esc-media-preview img{display:block;max-width:260px;max-height:160px;object-fit:contain}.esc-news-create .esc-news-help{color:#50575e}.esc-news-create .wp-editor-wrap{margin-top:8px}' );
    wp_add_inline_script( 'media-editor', "document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('[data-esc-news-media]').forEach(function(button){button.addEventListener('click',function(e){e.preventDefault();var id=document.getElementById(button.dataset.targetId),url=document.getElementById(button.dataset.targetUrl),preview=document.getElementById(button.dataset.targetPreview),frame=wp.media({title:'Bild auswählen',button:{text:'Bild verwenden'},multiple:false});frame.on('select',function(){var a=frame.state().get('selection').first().toJSON();id.value=a.id;url.value=a.url;preview.innerHTML='<img src=\\\"'+a.url+'\\\" alt=\\\"\\\">';});frame.open();});});});" );
}
add_action( 'admin_enqueue_scripts', 'esc_river_rats_news_editor_assets' );

function esc_river_rats_news_editor_page() {
    if ( ! current_user_can( 'edit_posts' ) ) { wp_die( 'Keine Berechtigung.' ); }
    $areas = esc_river_rats_news_editor_areas();
    $selected = sanitize_key( $_GET['news_area'] ?? '' );
    if ( ! isset( $areas[ $selected ] ) ) { foreach ( $areas as $slug => $label ) { if ( current_user_can( 'esc_create_news_' . str_replace( '-', '_', $slug ) ) ) { $selected = $slug; break; } } }
    if ( ! $selected || ! current_user_can( 'esc_create_news_' . str_replace( '-', '_', $selected ) ) ) { echo '<div class="wrap esc-news-create"><h1>News erstellen</h1><p>Für deinen Benutzer ist aktuell kein News-Bereich freigeschaltet.</p></div>'; return; }
    $label = $areas[ $selected ]; $nonce = wp_create_nonce( 'esc_create_news' );
    ?><div class="wrap esc-news-create"><h1><?php echo esc_html( $label ); ?> – News erstellen</h1><p class="description">Erstelle eine Meldung für den Bereich <?php echo esc_html( $label ); ?>. Das Erscheinungsbild wird automatisch vom ESC-Theme vorgegeben.</p><form class="esc-news-form" method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>"><input type="hidden" name="action" value="esc_create_news"><input type="hidden" name="news_area" value="<?php echo esc_attr( $selected ); ?>"><input type="hidden" name="_wpnonce" value="<?php echo esc_attr( $nonce ); ?>"><p><label for="esc-news-title"><strong>Titel</strong></label><input required class="large-text" type="text" id="esc-news-title" name="news_title" value=""></p><p><strong>Beitragsfoto</strong></p><p><button type="button" class="button" data-esc-news-media data-target-id="esc-news-featured-id" data-target-url="esc-news-featured-url" data-target-preview="esc-news-featured-preview">Bild auswählen</button><input type="hidden" id="esc-news-featured-id" name="featured_id" value=""><input type="hidden" id="esc-news-featured-url" value=""><span class="esc-media-preview" id="esc-news-featured-preview"></span></p><p><strong>Foto für den Beitragstext</strong></p><p class="esc-news-help">Optionales Bild innerhalb des Beitrags. Wenn leer, wird automatisch das Beitragsfoto verwendet.</p><p><button type="button" class="button" data-esc-news-media data-target-id="esc-news-inline-id" data-target-url="esc-news-inline-url" data-target-preview="esc-news-inline-preview">Bild auswählen</button><input type="hidden" id="esc-news-inline-id" name="inline_id" value=""><input type="hidden" id="esc-news-inline-url" value=""><span class="esc-media-preview" id="esc-news-inline-preview"></span></p><p><label for="esc-news-content"><strong>Beitragstext</strong></label><?php wp_editor( '', 'esc_news_content', array( 'textarea_name' => 'news_content', 'media_buttons' => false, 'quicktags' => false, 'teeny' => true, 'tinymce' => array( 'toolbar1' => 'bold,underline,styleselect,removeformat', 'toolbar2' => '', 'style_formats' => array( array( 'title' => 'Großbuchstaben', 'inline' => 'span', 'classes' => 'esc-text-uppercase' ) ), 'menubar' => false, 'statusbar' => false ) ) ); ?></p><p><button class="button button-primary" type="submit">News veröffentlichen</button></p></form></div><?php
}

function esc_river_rats_create_news_admin() {
    $area = sanitize_key( $_POST['news_area'] ?? '' ); $areas = esc_river_rats_news_editor_areas(); $cap = 'esc_create_news_' . str_replace( '-', '_', $area );
    if ( ! isset( $areas[ $area ] ) || ! current_user_can( $cap ) || ! check_admin_referer( 'esc_create_news' ) ) { wp_die( 'Keine Berechtigung oder ungültige Anfrage.' ); }
    $title = sanitize_text_field( wp_unslash( $_POST['news_title'] ?? '' ) ); $content = wp_kses_post( wp_unslash( $_POST['news_content'] ?? '' ) );
    if ( ! $title ) { wp_safe_redirect( admin_url( 'admin.php?page=esc-news-create&news_area=' . rawurlencode( $area ) . '&error=title' ) ); exit; }
    $category = get_category_by_slug( $area ); if ( ! $category ) { $created = wp_insert_term( $areas[ $area ], 'category', array( 'slug' => $area ) ); $category_id = is_wp_error( $created ) ? 0 : (int) $created['term_id']; } else { $category_id = (int) $category->term_id; }
    $post_id = wp_insert_post( array( 'post_title' => $title, 'post_content' => $content, 'post_status' => 'publish', 'post_type' => 'post', 'post_category' => $category_id ? array( $category_id ) : array() ), true );
    if ( is_wp_error( $post_id ) ) { wp_die( esc_html( $post_id->get_error_message() ) ); }
    $featured_id = absint( $_POST['featured_id'] ?? 0 ); $inline_id = absint( $_POST['inline_id'] ?? 0 );
    if ( $featured_id ) { set_post_thumbnail( $post_id, $featured_id ); }
    update_post_meta( $post_id, '_esc_news_inline_image_id', $inline_id ?: $featured_id );
    wp_safe_redirect( admin_url( 'edit.php?post_type=post&esc_news_created=1' ) ); exit;
}
add_action( 'admin_post_esc_create_news', 'esc_river_rats_create_news_admin' );

function esc_river_rats_news_inline_image( $content ) {
    if ( is_admin() || ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() ) { return $content; }
    $image_id = absint( get_post_meta( get_the_ID(), '_esc_news_inline_image_id', true ) );
    if ( ! $image_id ) { return $content; }
    $image = wp_get_attachment_image( $image_id, 'large', false, array( 'class' => 'esc-news-inline-image' ) );
    return $image ? '<figure class="esc-news-inline-image-wrap">' . $image . '</figure>' . $content : $content;
}
add_filter( 'the_content', 'esc_river_rats_news_inline_image', 25 );

/* Protected frontend composer for installations where SSO does not preserve
 * deep links into wp-admin. The existing backend editor remains available. */
function esc_river_rats_frontend_news_editor() {
    $path = trim( (string) parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ), '/' );
    if ( 'news-erstellen' !== $path ) { return; }
    if ( ! is_user_logged_in() ) { auth_redirect(); exit; }
    status_header( 200 );
    add_filter( 'pre_get_document_title', 'esc_river_rats_frontend_news_title' );

    if ( 'POST' === ( $_SERVER['REQUEST_METHOD'] ?? '' ) && 'esc_frontend_create_news' === ( $_POST['action'] ?? '' ) ) {
        esc_river_rats_frontend_create_news();
    }

    $areas = esc_river_rats_news_editor_areas();
    $allowed = array();
    foreach ( $areas as $slug => $label ) {
        if ( current_user_can( 'esc_create_news_' . str_replace( '-', '_', $slug ) ) ) { $allowed[ $slug ] = $label; }
    }
    if ( ! $allowed ) { wp_die( 'Für deinen Benutzer ist kein News-Bereich freigeschaltet.' ); }
    $selected = sanitize_key( $_GET['news_area'] ?? array_key_first( $allowed ) );
    if ( ! isset( $allowed[ $selected ] ) ) { $selected = array_key_first( $allowed ); }
    $notice = isset( $_GET['created'] ) ? '<div class="esc-news-frontend-notice">Die News wurde erfolgreich veröffentlicht.</div>' : '';

    get_header();
    echo '<main class="section shell esc-news-frontend"><div class="esc-news-frontend__intro"><p class="eyebrow">ESC RIVER RATS · REDAKTION</p><h1>News erstellen</h1><p>Erstelle eine Meldung im festen ESC-Design. Layout, Farben und Schriften werden automatisch vorgegeben.</p></div>' . $notice . '<form class="esc-news-frontend__form" method="post" action="' . esc_url( home_url( '/news-erstellen/' ) ) . '" enctype="multipart/form-data"><input type="hidden" name="action" value="esc_frontend_create_news"><input type="hidden" name="_wpnonce" value="' . esc_attr( wp_create_nonce( 'esc_frontend_create_news' ) ) . '"><p><label for="esc-front-area">Bereich</label><select id="esc-front-area" name="news_area">';
    foreach ( $allowed as $slug => $label ) { echo '<option value="' . esc_attr( $slug ) . '" ' . selected( $selected, $slug, false ) . '>' . esc_html( $label ) . '</option>'; }
    echo '</select></p><p><label for="esc-front-title">Titel</label><input required type="text" id="esc-front-title" name="news_title"></p><p><label for="esc-front-featured">Beitragsfoto</label><input type="file" accept="image/*" id="esc-front-featured" name="featured_image" data-min-width="1600" data-min-height="900"><small>Mindestens 1600 × 900 Pixel, optimal 1920 × 1080. Zu kleine oder ungeeignete Bilder werden nicht zugelassen.</small><span class="esc-image-validation" id="esc-front-featured-check" role="status"></span></p><p><label for="esc-front-inline">Foto für den Beitragstext</label><input type="file" accept="image/*" id="esc-front-inline" name="inline_image" data-min-width="1600" data-min-height="900"><small>Optionales Querformat, mindestens 1600 × 900 Pixel. Wenn leer, wird automatisch das Beitragsfoto verwendet.</small><span class="esc-image-validation" id="esc-front-inline-check" role="status"></span></p><div class="esc-news-editor"><label for="esc-front-content">Beitragstext</label><div class="esc-news-toolbar" role="toolbar" aria-label="Textformatierung"><button type="button" data-command="bold"><strong>Fett</strong></button><button type="button" data-command="underline"><u>Unterstrichen</u></button><button type="button" data-command="uppercase">Großbuchstaben</button></div><div id="esc-front-content" class="esc-news-editor__area" contenteditable="true" role="textbox" aria-multiline="true"></div><textarea required name="news_content" id="esc-front-content-value" hidden></textarea></div><p><button class="button button-primary" type="submit">News veröffentlichen</button></p></form></main><script>(function(){var area=document.getElementById("esc-front-content"),value=document.getElementById("esc-front-content-value");if(!area)return;document.querySelectorAll("[data-command]").forEach(function(button){button.addEventListener("click",function(){area.focus();if(button.dataset.command==="uppercase"){var s=window.getSelection();if(s&&s.rangeCount&&!s.isCollapsed){document.execCommand("insertHTML",false,"<span class=\\"esc-text-uppercase\\">"+s.toString()+"</span>");}}else{document.execCommand(button.dataset.command,false,null);}});});var form=area.closest("form"),validImages=true;document.querySelectorAll("input[type=file][data-min-width]").forEach(function(input){input.addEventListener("change",function(){var check=document.getElementById(input.id+"-check"),file=input.files[0];if(!file){check.textContent="";return;}var image=new Image();image.onload=function(){var ok=image.width>=+input.dataset.minWidth&&image.height>=+input.dataset.minHeight&&(image.width/image.height)>=1.45&&(image.width/image.height)<=2.05;check.textContent=ok?"Bild geeignet: "+image.width+" × "+image.height+" Pixel":"Bild zu klein oder ungeeignet. Bitte ein Querformat ab 1600 × 900 Pixel wählen.";check.className="esc-image-validation "+(ok?"is-valid":"is-invalid");input.dataset.valid=ok?"1":"0";URL.revokeObjectURL(image.src);};image.onerror=function(){check.textContent="Bitte eine gültige Bilddatei wählen.";check.className="esc-image-validation is-invalid";input.dataset.valid="0";};image.src=URL.createObjectURL(file);});});form.addEventListener("submit",function(event){var invalid=[].some.call(form.querySelectorAll("input[type=file][data-min-width]"),function(input){return input.files.length&&input.dataset.valid!=="1";});if(invalid){event.preventDefault();alert("Bitte korrigiere zuerst die markierten Bilddateien.");}value.value=area.innerHTML;});})();</script>';
    get_footer(); exit;
}
add_action( 'template_redirect', 'esc_river_rats_frontend_news_editor', 1 );

function esc_river_rats_frontend_news_title() { return 'News erstellen · ESC River Rats Geretsried e.V.'; }

function esc_river_rats_frontend_spellcheck() {
    $path = trim( (string) parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ), '/' );
    if ( 'news-erstellen' !== $path ) { return; }
    echo '<script>(function(){var fields=document.querySelectorAll("#esc-front-content,#esc-front-title");fields.forEach(function(field){field.setAttribute("spellcheck","true");field.setAttribute("lang","de-DE");});})();</script>';
}
add_action( 'wp_footer', 'esc_river_rats_frontend_spellcheck', 30 );

function esc_river_rats_validate_news_image( $key, $label, $min_width = 1600, $min_height = 900 ) {
    if ( empty( $_FILES[ $key ]['name'] ) ) { return true; }
    if ( ! empty( $_FILES[ $key ]['error'] ) ) { return new WP_Error( 'image_upload', $label . ': Die Datei konnte nicht gelesen werden.' ); }
    $size = @getimagesize( $_FILES[ $key ]['tmp_name'] );
    if ( ! $size || empty( $size[0] ) || empty( $size[1] ) ) { return new WP_Error( 'image_type', $label . ': Bitte eine gültige Bilddatei auswählen.' ); }
    if ( $size[0] < $min_width || $size[1] < $min_height ) { return new WP_Error( 'image_small', sprintf( '%s ist zu klein. Bitte mindestens %d × %d Pixel verwenden (optimal: 1920 × 1080 Pixel).', $label, $min_width, $min_height ) ); }
    $ratio = $size[0] / $size[1];
    if ( $ratio < 1.45 || $ratio > 2.05 ) { return new WP_Error( 'image_ratio', $label . ': Bitte ein Querformat verwenden. Das Bild sollte ungefähr dem Verhältnis 16:9 entsprechen.' ); }
    return true;
}

function esc_river_rats_optimize_news_image( $attachment_id ) {
    if ( ! $attachment_id ) { return; }
    $file = get_attached_file( $attachment_id );
    if ( ! $file || ! file_exists( $file ) ) { return; }
    $editor = wp_get_image_editor( $file );
    if ( is_wp_error( $editor ) ) { return; }
    $editor->resize( 2400, 2400, false );
    $editor->set_quality( 82 );
    $editor->save( $file );
    wp_update_attachment_metadata( $attachment_id, wp_generate_attachment_metadata( $attachment_id, $file ) );
}

function esc_river_rats_frontend_create_news() {
    if ( ! is_user_logged_in() || ! check_admin_referer( 'esc_frontend_create_news' ) ) { wp_die( 'Ungültige Anfrage.' ); }
    $area = sanitize_key( $_POST['news_area'] ?? '' );
    $areas = esc_river_rats_news_editor_areas();
    $cap = 'esc_create_news_' . str_replace( '-', '_', $area );
    if ( ! isset( $areas[ $area ] ) || ! current_user_can( $cap ) ) { wp_die( 'Für diesen News-Bereich besteht keine Berechtigung.' ); }
    foreach ( array( 'featured_image' => 'Das Beitragsfoto', 'inline_image' => 'Das Textfoto' ) as $image_key => $image_label ) {
        $image_check = esc_river_rats_validate_news_image( $image_key, $image_label );
        if ( is_wp_error( $image_check ) ) { wp_die( esc_html( $image_check->get_error_message() ) ); }
    }
    $title = sanitize_text_field( wp_unslash( $_POST['news_title'] ?? '' ) );
    $content = wp_kses( wp_unslash( $_POST['news_content'] ?? '' ), array( 'strong' => array(), 'b' => array(), 'u' => array(), 'span' => array( 'class' => array() ), 'p' => array(), 'br' => array(), 'em' => array() ) );
    if ( ! $title || ! trim( wp_strip_all_tags( $content ) ) ) { wp_die( 'Titel und Beitragstext sind erforderlich.' ); }
    $category = get_category_by_slug( $area );
    $post_id = wp_insert_post( array( 'post_title' => $title, 'post_content' => $content, 'post_status' => 'publish', 'post_type' => 'post', 'post_category' => $category ? array( (int) $category->term_id ) : array() ), true );
    if ( is_wp_error( $post_id ) ) { wp_die( esc_html( $post_id->get_error_message() ) ); }
    require_once ABSPATH . 'wp-admin/includes/file.php'; require_once ABSPATH . 'wp-admin/includes/media.php'; require_once ABSPATH . 'wp-admin/includes/image.php';
    $featured_id = ! empty( $_FILES['featured_image']['name'] ) ? media_handle_upload( 'featured_image', $post_id ) : 0;
    $inline_id = ! empty( $_FILES['inline_image']['name'] ) ? media_handle_upload( 'inline_image', $post_id ) : 0;
    if ( ! is_wp_error( $featured_id ) && $featured_id ) { set_post_thumbnail( $post_id, $featured_id ); } else { $featured_id = 0; }
    if ( is_wp_error( $inline_id ) || ! $inline_id ) { $inline_id = $featured_id; }
    esc_river_rats_optimize_news_image( $featured_id );
    if ( $inline_id !== $featured_id ) { esc_river_rats_optimize_news_image( $inline_id ); }
    update_post_meta( $post_id, '_esc_news_inline_image_id', (int) $inline_id );
    wp_safe_redirect( home_url( '/news-erstellen/?created=1&news_area=' . rawurlencode( $area ) ) ); exit;
}
add_action( 'admin_post_esc_frontend_create_news', 'esc_river_rats_frontend_create_news' );

/* Native WordPress posts in the Flashnews category power the header ticker. */
function esc_river_rats_render_flash_news() {
    $flash_news = new WP_Query( array(
        'post_type'           => 'post',
        'post_status'         => 'publish',
        'posts_per_page'      => 5,
        'category_name'       => 'flashnews',
        'no_found_rows'       => true,
        'ignore_sticky_posts' => true,
    ) );
    if ( ! $flash_news->have_posts() ) { return ''; }
    $items = array();
    while ( $flash_news->have_posts() ) {
        $flash_news->the_post();
        $target = get_post_meta( get_the_ID(), '_esc_flashnews_link', true );
        $label = esc_html( get_the_title() );
        $items[] = $target ? '<a href="' . esc_url( $target ) . '">' . $label . '</a>' : '<span>' . $label . '</span>';
    }
    wp_reset_postdata();
    return '<aside class="flashbar" aria-label="Flash-News"><div class="flashbar-track" aria-live="polite"><div class="flashbar-sequence"><strong>FLASH-NEWS</strong><span class="flashbar-items">' . implode( '<span class="flashbar-gap" aria-hidden="true"></span>', $items ) . '</span></div></div></aside>';
}

function esc_river_rats_register_flash_news_block() {
	register_block_type( get_theme_file_path( 'blocks/flash-news' ), array( 'render_callback' => 'esc_river_rats_render_flash_news' ) );
}
add_action( 'init', 'esc_river_rats_register_flash_news_block' );

function esc_river_rats_render_next_home_game() {
	$logo = get_theme_file_uri( 'assets/images/river-rats-logo.png' );
	return '<aside class="next-home-game" data-next-home-game aria-label="Nächstes Heimspiel"><div class="next-home-game__eyebrow">NÄCHSTES HEIMSPIEL</div><div class="next-home-game__loading">Spielplan wird geladen …</div><div class="next-home-game__content" hidden><div class="next-home-game__date"><span data-game-date></span><strong data-game-time></strong></div><div class="next-home-game__teams"><div class="next-home-game__team"><img src="' . esc_url( $logo ) . '" alt="River Rats" data-home-logo><strong data-home-name>RIVER RATS</strong></div><div class="next-home-game__score" aria-label="Spielstand noch offen">– : –</div><div class="next-home-game__team next-home-game__team--away"><img src="" alt="" data-away-logo hidden><strong data-away-name></strong></div></div><div class="next-home-game__venue" data-game-venue></div><a class="next-home-game__link" href="/river-rats/">SPIELPLAN ANSEHEN <span aria-hidden="true">→</span></a></div><div class="next-home-game__error" hidden>Das nächste Heimspiel findest du im Spielplan.</div></aside>';
}
function esc_river_rats_register_next_home_game_block() {
	register_block_type( get_theme_file_path( 'blocks/next-home-game' ), array( 'render_callback' => 'esc_river_rats_render_next_home_game' ) );
}
add_action( 'init', 'esc_river_rats_register_next_home_game_block' );

function esc_river_rats_flashnews_meta_box() {
    add_meta_box( 'esc-flashnews-settings', 'Flash-News-Einstellungen', 'esc_river_rats_flashnews_meta_box_html', 'post', 'normal', 'high' );
}
add_action( 'add_meta_boxes', 'esc_river_rats_flashnews_meta_box' );

function esc_river_rats_flashnews_meta_box_html( $post ) {
    wp_nonce_field( 'esc_flashnews_save', 'esc_flashnews_nonce' );
    $link = get_post_meta( $post->ID, '_esc_flashnews_link', true );
    echo '<p><label for="esc_flashnews_link"><strong>Ziel-Link (optional)</strong></label></p><p><input type="url" class="widefat" id="esc_flashnews_link" name="esc_flashnews_link" value="' . esc_attr( $link ) . '" placeholder="https://…"></p><p class="description">Nur für Beiträge der Kategorie Flashnews. Ohne Link wird die Meldung nicht anklickbar.</p>';
}

function esc_river_rats_save_flashnews_link( $post_id ) {
    if ( ! isset( $_POST['esc_flashnews_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['esc_flashnews_nonce'] ) ), 'esc_flashnews_save' ) ) { return; }
    if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) { return; }
    if ( ! current_user_can( 'edit_post', $post_id ) ) { return; }
    $categories = wp_get_post_categories( $post_id, array( 'fields' => 'slugs' ) );
    if ( in_array( 'flashnews', $categories, true ) && ! empty( $_POST['esc_flashnews_link'] ) ) {
        update_post_meta( $post_id, '_esc_flashnews_link', esc_url_raw( wp_unslash( $_POST['esc_flashnews_link'] ) ) );
    } else {
        delete_post_meta( $post_id, '_esc_flashnews_link' );
    }
}
add_action( 'save_post_post', 'esc_river_rats_save_flashnews_link' );

function esc_river_rats_flashnews_admin_ui( $hook ) {
    if ( ! in_array( $hook, array( 'post.php', 'post-new.php' ), true ) ) { return; }
    wp_add_inline_style( 'common', '.esc-flashnews-editor-hidden .editor-styles-wrapper,.esc-flashnews-editor-hidden .wp-block-post-content,.esc-flashnews-editor-hidden .edit-post-visual-editor__post-title-wrapper + div{display:none!important}.esc-flashnews-editor-hidden #postdivrich{display:none!important}.esc-flashnews-admin .esc-flashnews-form{max-width:720px;margin:24px 0;padding:24px;background:#fff;border:1px solid #dcdcde}.esc-flashnews-admin .esc-flashnews-form label{display:block;margin-bottom:7px}.esc-flashnews-admin .esc-flashnews-form input.regular-text{width:100%;max-width:620px}.esc-flashnews-admin fieldset label{display:inline-block;margin:8px 22px 8px 0}.esc-flashnews-admin h1{margin-bottom:4px}' );
    wp_add_inline_script( 'wp-edit-post', "(function(){function escFlashToggle(){var boxes=document.querySelectorAll('input[type=checkbox][name=post_category[]]');var active=false;boxes.forEach(function(box){var label=box.closest('label');if(label&&/Flashnews/i.test(label.textContent)){active=box.checked;}});document.body.classList.toggle('esc-flashnews-editor-hidden',active);}document.addEventListener('DOMContentLoaded',function(){escFlashToggle();document.addEventListener('change',function(e){if(e.target&&e.target.name==='post_category[]'){escFlashToggle();}});});})();" );
}
add_action( 'admin_enqueue_scripts', 'esc_river_rats_flashnews_admin_ui' );

function esc_river_rats_flashnews_admin_menu() {
    add_menu_page( 'Flash-News', 'Flash-News', 'edit_posts', 'esc-flashnews', 'esc_river_rats_flashnews_admin_page', 'dashicons-megaphone', 5 );
}
add_action( 'admin_menu', 'esc_river_rats_flashnews_admin_menu' );

function esc_river_rats_flashnews_admin_page() {
    if ( ! current_user_can( 'edit_posts' ) ) { wp_die( 'Keine Berechtigung.' ); }
    $items = get_posts( array( 'post_type' => 'post', 'post_status' => array( 'publish', 'draft', 'pending', 'private' ), 'posts_per_page' => 20, 'category_name' => 'flashnews', 'orderby' => 'date', 'order' => 'DESC' ) );
    ?>
    <div class="wrap esc-flashnews-admin"><h1>Flash-News</h1><p class="description">Kurze Meldungen für das Laufband. Es werden nur Überschrift und optionaler Ziel-Link verwendet.</p>
    <form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" class="esc-flashnews-form">
        <input type="hidden" name="action" value="esc_save_flashnews"><input type="hidden" name="_wp_http_referer" value="<?php echo esc_url( admin_url( 'admin.php?page=esc-flashnews' ) ); ?>"><?php wp_nonce_field( 'esc_save_flashnews' ); ?>
        <p><label for="esc-flashnews-title"><strong>Überschrift</strong></label><input required type="text" id="esc-flashnews-title" name="flashnews_title" class="regular-text" maxlength="180"></p>
        <p><label for="esc-flashnews-link"><strong>Ziel-Link (optional)</strong></label><input type="url" id="esc-flashnews-link" name="flashnews_link" class="regular-text" placeholder="https://…"></p>
        <fieldset><legend><strong>Status</strong></legend><label><input type="radio" name="flashnews_status" value="draft" checked> Entwurf</label><label><input type="radio" name="flashnews_status" value="publish"> Veröffentlicht</label></fieldset>
        <p><button class="button button-primary" type="submit">Speichern</button></p>
    </form>
    <h2>Vorhandene Flash-News</h2><table class="widefat striped"><thead><tr><th>Überschrift</th><th>Status</th><th>Datum</th><th>Aktion</th></tr></thead><tbody>
    <?php if ( ! $items ) : ?><tr><td colspan="4">Noch keine Flash-News vorhanden.</td></tr><?php else : foreach ( $items as $item ) : ?><tr><td><?php echo esc_html( get_the_title( $item ) ); ?></td><td><?php echo esc_html( get_post_status_object( $item->post_status )->label ); ?></td><td><?php echo esc_html( get_the_date( '', $item ) ); ?></td><td><a class="button" href="<?php echo esc_url( wp_nonce_url( admin_url( 'admin-post.php?action=esc_flashnews_archive&post_id=' . $item->ID ), 'esc_flashnews_archive_' . $item->ID ) ); ?>">Deaktivieren</a> <a class="button-link-delete" href="<?php echo esc_url( wp_nonce_url( admin_url( 'admin-post.php?action=esc_flashnews_trash&post_id=' . $item->ID ), 'esc_flashnews_trash_' . $item->ID ) ); ?>">Papierkorb</a></td></tr><?php endforeach; endif; ?></tbody></table></div>
    <?php
}

function esc_river_rats_save_flashnews_admin() {
    if ( ! current_user_can( 'edit_posts' ) || ! check_admin_referer( 'esc_save_flashnews' ) ) { wp_die( 'Ungültige Anfrage.' ); }
    $title = isset( $_POST['flashnews_title'] ) ? sanitize_text_field( wp_unslash( $_POST['flashnews_title'] ) ) : '';
    $link = isset( $_POST['flashnews_link'] ) ? esc_url_raw( wp_unslash( $_POST['flashnews_link'] ) ) : '';
    $status = isset( $_POST['flashnews_status'] ) && 'publish' === $_POST['flashnews_status'] ? 'publish' : 'draft';
    $term = get_term_by( 'slug', 'flashnews', 'category' );
    if ( ! $title || ! $term ) { wp_safe_redirect( admin_url( 'admin.php?page=esc-flashnews' ) ); exit; }
    $post_id = wp_insert_post( array( 'post_title' => $title, 'post_content' => '', 'post_status' => $status, 'post_type' => 'post', 'post_category' => array( (int) $term->term_id ), 'comment_status' => 'closed', 'ping_status' => 'closed' ), true );
    if ( ! is_wp_error( $post_id ) && $link ) { update_post_meta( $post_id, '_esc_flashnews_link', $link ); }
    wp_safe_redirect( admin_url( 'admin.php?page=esc-flashnews&saved=1' ) ); exit;
}
add_action( 'admin_post_esc_save_flashnews', 'esc_river_rats_save_flashnews_admin' );

function esc_river_rats_archive_flashnews_admin() {
    $post_id = absint( $_GET['post_id'] ?? 0 );
    if ( ! current_user_can( 'edit_post', $post_id ) || ! check_admin_referer( 'esc_flashnews_archive_' . $post_id ) ) { wp_die( 'Ungültige Anfrage.' ); }
    wp_update_post( array( 'ID' => $post_id, 'post_status' => 'draft' ) ); wp_safe_redirect( admin_url( 'admin.php?page=esc-flashnews' ) ); exit;
}
add_action( 'admin_post_esc_flashnews_archive', 'esc_river_rats_archive_flashnews_admin' );

function esc_river_rats_trash_flashnews_admin() {
    $post_id = absint( $_GET['post_id'] ?? 0 );
    if ( ! current_user_can( 'delete_post', $post_id ) || ! check_admin_referer( 'esc_flashnews_trash_' . $post_id ) ) { wp_die( 'Ungültige Anfrage.' ); }
    wp_trash_post( $post_id ); wp_safe_redirect( admin_url( 'admin.php?page=esc-flashnews' ) ); exit;
}
add_action( 'admin_post_esc_flashnews_trash', 'esc_river_rats_trash_flashnews_admin' );

function esc_river_rats_disable_flashnews_block_editor( $use_block_editor, $post ) {
    return $post && 'post' === $post->post_type && has_category( 'flashnews', $post ) ? false : $use_block_editor;
}
add_filter( 'use_block_editor_for_post', 'esc_river_rats_disable_flashnews_block_editor', 10, 2 );

/* Native sponsor records and the small editorial form used by the homepage band. */
function esc_river_rats_register_sponsor_type() {
	register_post_type( 'esc_sponsor', array(
		'labels' => array( 'name' => 'Sponsoren', 'singular_name' => 'Sponsor' ),
		'public' => false, 'show_ui' => false, 'show_in_menu' => false,
		'supports' => array( 'title' ), 'map_meta_cap' => true,
	) );
}
add_action( 'init', 'esc_river_rats_register_sponsor_type' );

function esc_river_rats_sponsor_seed_data() {
	return array(
		'edeka-heininger' => array( 'Edeka Heininger', 'https://www.edeka-heininger-dietz.de' ),
		'ehgartner-entsorgung' => array( 'Ehgartner Entsorgung', 'https://www.ehgartner.de' ),
		'energie-suedbayern' => array( 'Energie Südbayern', 'https://www.esb.de' ),
		'sparkasse' => array( 'Sparkasse', 'https://www.spktw.de' ),
		'ipe-dach' => array( 'IPE D.A.CH', 'https://www.institutional-investment.de' ),
		'elektro-friedl' => array( 'Elektro Friedl GmbH', 'https://www.ep.de' ),
	);
}

function esc_river_rats_sponsor_label( $key ) {
	$known = esc_river_rats_sponsor_seed_data();
	if ( isset( $known[ $key ] ) ) { return $known[ $key ][0]; }
	return ucwords( str_replace( '-', ' ', $key ) );
}

function esc_river_rats_seed_sponsors() {
	if ( get_option( 'esc_river_rats_sponsors_seeded' ) ) { return; }
	$dir = get_theme_file_path( 'assets/images/sponsors' );
	$files = is_dir( $dir ) ? glob( $dir . '/*' ) : array();
	$known = esc_river_rats_sponsor_seed_data();
	foreach ( $files as $file ) {
		$key = sanitize_title( pathinfo( $file, PATHINFO_FILENAME ) );
		if ( get_posts( array( 'post_type' => 'esc_sponsor', 'meta_key' => '_esc_sponsor_seed_key', 'meta_value' => $key, 'fields' => 'ids', 'numberposts' => 1 ) ) ) { continue; }
		$id = wp_insert_post( array( 'post_type' => 'esc_sponsor', 'post_title' => esc_river_rats_sponsor_label( $key ), 'post_status' => 'publish' ), true );
		if ( is_wp_error( $id ) ) { continue; }
		update_post_meta( $id, '_esc_sponsor_seed_key', $key );
		update_post_meta( $id, '_esc_sponsor_logo', get_theme_file_uri( 'assets/images/sponsors/' . basename( $file ) ) );
		if ( isset( $known[ $key ][1] ) ) { update_post_meta( $id, '_esc_sponsor_url', esc_url_raw( $known[ $key ][1] ) ); }
	}
	update_option( 'esc_river_rats_sponsors_seeded', 1, false );
}
add_action( 'after_switch_theme', 'esc_river_rats_seed_sponsors' );
add_action( 'init', 'esc_river_rats_seed_sponsors', 30 );

function esc_river_rats_render_sponsors() {
	$sponsors = get_posts( array( 'post_type' => 'esc_sponsor', 'post_status' => 'publish', 'numberposts' => -1, 'orderby' => 'menu_order date', 'order' => 'ASC' ) );
	if ( ! $sponsors ) { return ''; }
	$cards = array();
	foreach ( $sponsors as $sponsor ) {
		$name = get_the_title( $sponsor );
		$logo = get_post_meta( $sponsor->ID, '_esc_sponsor_logo', true );
		$url = get_post_meta( $sponsor->ID, '_esc_sponsor_url', true );
		$card = '<span class="partner-card">' . ( $logo ? '<img src="' . esc_url( $logo ) . '" alt="' . esc_attr( $name ) . '" loading="lazy">' : '' ) . '<span>' . esc_html( $name ) . '</span></span>';
		if ( $url ) { $card = '<a class="partner-card" href="' . esc_url( $url ) . '" target="_blank" rel="noopener">' . ( $logo ? '<img src="' . esc_url( $logo ) . '" alt="' . esc_attr( $name ) . '" loading="lazy">' : '' ) . '<span>' . esc_html( $name ) . '</span></a>'; }
		$cards[] = $card;
	}
	$sequence = implode( '', $cards );
	return '<section class="partners" aria-label="Unsere Partner"><div class="shell"><div class="section-heading"><h2>Unsere Partner</h2><a class="partners-all" href="' . esc_url( home_url( '/sponsoren/' ) ) . '">Alle Sponsoren →</a></div><div class="partner-band"><div class="partner-band__track"><div class="partner-band__items">' . $sequence . '</div><div class="partner-band__items" aria-hidden="true">' . $sequence . '</div></div></div></div></section>';
}

/* The public sponsors page is generated from the same records as the homepage band. */
function esc_river_rats_render_sponsors_directory() {
	$sponsors = get_posts( array( 'post_type' => 'esc_sponsor', 'post_status' => 'publish', 'numberposts' => -1, 'orderby' => 'menu_order date', 'order' => 'ASC' ) );
	if ( ! $sponsors ) { return ''; }
	$items = array();
	foreach ( $sponsors as $sponsor ) {
		$name = get_the_title( $sponsor );
		$logo = get_post_meta( $sponsor->ID, '_esc_sponsor_logo', true );
		$url  = get_post_meta( $sponsor->ID, '_esc_sponsor_url', true );
		$visual = ( $logo ? '<img src="' . esc_url( $logo ) . '" alt="' . esc_attr( $name ) . '" loading="lazy">' : '' ) . '<span>' . esc_html( $name ) . '</span>';
		$items[] = $url ? '<a class="sponsor-directory-card" href="' . esc_url( $url ) . '" target="_blank" rel="noopener">' . $visual . '</a>' : '<div class="sponsor-directory-card">' . $visual . '</div>';
	}
	return '<section class="sponsor-directory" aria-labelledby="sponsor-directory-title"><div class="sponsor-directory__heading"><p class="eyebrow">ESC PARTNER</p><h2 id="sponsor-directory-title">Unsere Sponsoren</h2></div><div class="sponsor-directory__grid">' . implode( '', $items ) . '</div></section>';
}

function esc_river_rats_append_sponsors_directory( $content ) {
	if ( is_admin() || ! is_singular( 'page' ) || ! is_page( 'sponsoren' ) || ! in_the_loop() || ! is_main_query() ) { return $content; }
	$directory = esc_river_rats_render_sponsors_directory();
	return $directory ? $content . '<div class="sponsor-directory-spacer" aria-hidden="true"></div>' . $directory : $content;
}
add_filter( 'the_content', 'esc_river_rats_append_sponsors_directory', 20 );

function esc_river_rats_register_sponsors_block() {
	register_block_type( get_theme_file_path( 'blocks/sponsors' ), array( 'render_callback' => 'esc_river_rats_render_sponsors' ) );
}
add_action( 'init', 'esc_river_rats_register_sponsors_block' );

function esc_river_rats_sponsors_admin_menu() {
	add_menu_page( 'Sponsoren', 'Sponsoren', 'edit_posts', 'esc-sponsors', 'esc_river_rats_sponsors_list_page', 'dashicons-groups', 6 );
	add_submenu_page( 'esc-sponsors', 'Alle Sponsoren', 'Alle Sponsoren', 'edit_posts', 'esc-sponsors', 'esc_river_rats_sponsors_list_page' );
	add_submenu_page( 'esc-sponsors', 'Neu hinzufügen', 'Neu hinzufügen', 'edit_posts', 'esc-sponsor-new', 'esc_river_rats_sponsor_form_page' );
}
add_action( 'admin_menu', 'esc_river_rats_sponsors_admin_menu' );

function esc_river_rats_sponsors_admin_assets( $hook ) {
	if ( false === strpos( $hook, 'esc-sponsor' ) ) { return; }
	wp_enqueue_media();
	wp_add_inline_script( 'media-editor', "document.addEventListener('DOMContentLoaded',function(){var b=document.querySelector('[data-esc-media]'),i=document.querySelector('[data-esc-media-id]'),u=document.querySelector('[data-esc-media-url]'),p=document.querySelector('[data-esc-media-preview]');if(!b)return;b.addEventListener('click',function(e){e.preventDefault();var f=wp.media({title:'Logo auswählen',button:{text:'Logo verwenden'},multiple:false});f.on('select',function(){var a=f.state().get('selection').first().toJSON();i.value=a.id;u.value=a.url;p.innerHTML='<img src=\"'+a.url+'\" alt=\"\" style=\"max-width:240px;max-height:100px;object-fit:contain\">';});f.open();});});" );
}
add_action( 'admin_enqueue_scripts', 'esc_river_rats_sponsors_admin_assets' );

function esc_river_rats_sponsors_list_page() {
	if ( ! current_user_can( 'edit_posts' ) ) { wp_die( 'Keine Berechtigung.' ); }
	$items = get_posts( array( 'post_type' => 'esc_sponsor', 'post_status' => array( 'publish', 'draft' ), 'numberposts' => -1, 'orderby' => 'menu_order date', 'order' => 'ASC' ) );
	?><div class="wrap esc-sponsors-admin"><h1>Sponsoren <a class="page-title-action" href="<?php echo esc_url( admin_url( 'admin.php?page=esc-sponsor-new' ) ); ?>">Neu hinzufügen</a></h1><p>Aktive Sponsoren erscheinen automatisch im Sponsorenband der Homepage.</p><table class="widefat striped"><thead><tr><th>Logo</th><th>Firmenname</th><th>Website</th><th>Status</th><th>Aktion</th></tr></thead><tbody><?php if ( ! $items ) : ?><tr><td colspan="5">Noch keine Sponsoren vorhanden.</td></tr><?php else : foreach ( $items as $item ) : ?><tr><td><?php $logo = get_post_meta( $item->ID, '_esc_sponsor_logo', true ); echo $logo ? '<img src="' . esc_url( $logo ) . '" alt="" style="max-width:100px;max-height:42px;object-fit:contain">' : '—'; ?></td><td><strong><?php echo esc_html( get_the_title( $item ) ); ?></strong></td><td><?php echo esc_html( get_post_meta( $item->ID, '_esc_sponsor_url', true ) ); ?></td><td><?php echo 'publish' === $item->post_status ? 'Aktiv' : 'Inaktiv'; ?></td><td><a class="button" href="<?php echo esc_url( admin_url( 'admin.php?page=esc-sponsor-new&sponsor_id=' . $item->ID ) ); ?>">Bearbeiten</a></td></tr><?php endforeach; endif; ?></tbody></table></div><?php
}

function esc_river_rats_sponsor_form_page() {
	if ( ! current_user_can( 'edit_posts' ) ) { wp_die( 'Keine Berechtigung.' ); }
	$id = absint( $_GET['sponsor_id'] ?? 0 ); $item = $id ? get_post( $id ) : null;
	$title = $item ? $item->post_title : ''; $logo = $item ? get_post_meta( $id, '_esc_sponsor_logo', true ) : ''; $logo_id = $item ? get_post_meta( $id, '_esc_sponsor_logo_id', true ) : ''; $url = $item ? get_post_meta( $id, '_esc_sponsor_url', true ) : ''; $active = ! $item || 'publish' === $item->post_status;
	?><div class="wrap esc-sponsors-admin"><h1><?php echo $item ? 'Sponsor bearbeiten' : 'Neuer Sponsor'; ?></h1><form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" class="esc-sponsor-form" style="max-width:720px;background:#fff;border:1px solid #dcdcde;padding:24px;margin-top:20px"><input type="hidden" name="action" value="esc_save_sponsor"><input type="hidden" name="sponsor_id" value="<?php echo esc_attr( $id ); ?>"><?php wp_nonce_field( 'esc_save_sponsor' ); ?><p><label for="esc-sponsor-name"><strong>Firmenname</strong></label><br><input required class="large-text" type="text" id="esc-sponsor-name" name="sponsor_name" value="<?php echo esc_attr( $title ); ?>"></p><p><strong>Logo</strong><br><button type="button" class="button" data-esc-media>Bild auswählen</button><input type="hidden" name="sponsor_logo_id" data-esc-media-id value="<?php echo esc_attr( $logo_id ); ?>"><input type="hidden" name="sponsor_logo" data-esc-media-url value="<?php echo esc_attr( $logo ); ?>"><span data-esc-media-preview style="display:block;margin-top:12px"><?php echo $logo ? '<img src="' . esc_url( $logo ) . '" alt="" style="max-width:240px;max-height:100px;object-fit:contain">' : ''; ?></span></p><p><label for="esc-sponsor-url"><strong>Website</strong></label><br><input class="large-text" type="url" id="esc-sponsor-url" name="sponsor_url" value="<?php echo esc_attr( $url ); ?>" placeholder="https://…"></p><fieldset><legend><strong>Status</strong></legend><label><input type="radio" name="sponsor_status" value="publish" <?php checked( $active ); ?>> Aktiv</label> <label><input type="radio" name="sponsor_status" value="draft" <?php checked( ! $active ); ?>> Inaktiv</label></fieldset><p><button class="button button-primary" type="submit">Speichern</button></p></form></div><?php
}

function esc_river_rats_save_sponsor_admin() {
	if ( ! current_user_can( 'edit_posts' ) || ! check_admin_referer( 'esc_save_sponsor' ) ) { wp_die( 'Ungültige Anfrage.' ); }
	$id = absint( $_POST['sponsor_id'] ?? 0 ); $data = array( 'post_type' => 'esc_sponsor', 'post_title' => sanitize_text_field( wp_unslash( $_POST['sponsor_name'] ?? '' ) ), 'post_status' => 'publish' === ( $_POST['sponsor_status'] ?? '' ) ? 'publish' : 'draft' );
	if ( ! $data['post_title'] ) { wp_safe_redirect( admin_url( 'admin.php?page=esc-sponsor-new' ) ); exit; }
	if ( $id ) { $data['ID'] = $id; $id = wp_update_post( $data, true ); } else { $id = wp_insert_post( $data, true ); }
	if ( ! is_wp_error( $id ) ) { update_post_meta( $id, '_esc_sponsor_logo_id', absint( $_POST['sponsor_logo_id'] ?? 0 ) ); update_post_meta( $id, '_esc_sponsor_logo', esc_url_raw( wp_unslash( $_POST['sponsor_logo'] ?? '' ) ) ); update_post_meta( $id, '_esc_sponsor_url', esc_url_raw( wp_unslash( $_POST['sponsor_url'] ?? '' ) ) ); }
	wp_safe_redirect( admin_url( 'admin.php?page=esc-sponsors' ) ); exit;
}
add_action( 'admin_post_esc_save_sponsor', 'esc_river_rats_save_sponsor_admin' );

/* Homepage community cards are theme-owned content, editable through ESC only. */
function esc_river_rats_community_defaults() {
	return array(
		'eyebrow' => 'GEMEINSCHAFT', 'title' => 'WERDE TEIL DER RIVER RATS',
		'cards' => array(
			array( 'yellow' => 'MITGLIED WERDEN', 'white' => '', 'text' => 'Den ESC und das Vereinsleben aktiv mittragen.', 'url' => '/mitgliedschaft/' ),
			array( 'yellow' => 'MITHELFEN', 'white' => '', 'text' => 'Deine Erfahrung und Zeit für den Verein einbringen.', 'url' => '/mithelfen/' ),
			array( 'yellow' => 'FÖRDERVEREIN', 'white' => '', 'text' => 'Nachwuchs und Eishockey gezielt unterstützen.', 'url' => '/foerderverein/' ),
			array( 'yellow' => 'PARTNER WERDEN', 'white' => '', 'text' => 'Als Unternehmen sichtbar an der Seite des ESC stehen.', 'url' => '/sponsoren/' ),
		),
	);
}
function esc_river_rats_get_community() {
	$saved = get_option( 'esc_river_rats_community', array() );
	return wp_parse_args( is_array( $saved ) ? $saved : array(), esc_river_rats_community_defaults() );
}
function esc_river_rats_render_community() {
	$data = esc_river_rats_get_community(); $cards = '';
	foreach ( $data['cards'] as $card ) {
		$inner = '<span class="community-card__yellow">' . esc_html( $card['yellow'] ?? '' ) . '</span>' . ( ! empty( $card['white'] ) ? '<strong class="community-card__white">' . esc_html( $card['white'] ) . '</strong>' : '' ) . '<span class="community-card__text">' . esc_html( $card['text'] ?? '' ) . '</span>';
		$cards .= '<a class="community-card" href="' . esc_url( $card['url'] ?? '#' ) . '">' . $inner . '</a>';
	}
	return '<section class="community-section section--dark" aria-label="' . esc_attr( $data['eyebrow'] ) . '"><div class="shell"><p class="eyebrow">' . esc_html( $data['eyebrow'] ) . '</p><div class="section-heading"><h2>' . esc_html( $data['title'] ) . '</h2></div><div class="community-grid">' . $cards . '</div></div></section>';
}
function esc_river_rats_register_community_block() { register_block_type( get_theme_file_path( 'blocks/community' ), array( 'render_callback' => 'esc_river_rats_render_community' ) ); }
add_action( 'init', 'esc_river_rats_register_community_block' );
function esc_river_rats_ensure_community_defaults() { if ( false === get_option( 'esc_river_rats_community', false ) ) { add_option( 'esc_river_rats_community', esc_river_rats_community_defaults(), '', false ); } }
add_action( 'after_switch_theme', 'esc_river_rats_ensure_community_defaults' ); add_action( 'init', 'esc_river_rats_ensure_community_defaults', 30 );
function esc_river_rats_community_admin_menu() { add_menu_page( 'ESC', 'ESC', 'edit_posts', 'esc-community', 'esc_river_rats_community_admin_page', 'dashicons-admin-site-alt3', 4 ); add_submenu_page( 'esc-community', 'Gemeinschaft', 'Gemeinschaft', 'edit_posts', 'esc-community', 'esc_river_rats_community_admin_page' ); }
add_action( 'admin_menu', 'esc_river_rats_community_admin_menu' );
function esc_river_rats_community_admin_page() {
	if ( ! current_user_can( 'edit_posts' ) ) { wp_die( 'Keine Berechtigung.' ); } $data = esc_river_rats_get_community();
	?><div class="wrap esc-community-admin"><h1>Gemeinschaft</h1><p>Pflege nur die Inhalte der vier Homepage-Kacheln. Gestaltung und Layout bleiben im Theme.</p><form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" style="max-width:900px"><input type="hidden" name="action" value="esc_save_community"><input type="hidden" name="_wp_http_referer" value="<?php echo esc_url( admin_url( 'admin.php?page=esc-community' ) ); ?>"><?php wp_nonce_field( 'esc_save_community' ); ?><p><label><strong>Bereichsüberschrift</strong><br><input class="large-text" type="text" name="community_title" value="<?php echo esc_attr( $data['title'] ); ?>"></label></p><?php foreach ( $data['cards'] as $index => $card ) : ?><fieldset style="margin:20px 0;padding:18px;background:#fff;border:1px solid #dcdcde"><legend><strong>Kachel <?php echo esc_html( $index + 1 ); ?></strong></legend><p><label>Gelbe Überschrift<br><input class="large-text" type="text" name="cards[<?php echo esc_attr( $index ); ?>][yellow]" value="<?php echo esc_attr( $card['yellow'] ); ?>"></label></p><p><label>Weiße Überschrift<br><input class="large-text" type="text" name="cards[<?php echo esc_attr( $index ); ?>][white]" value="<?php echo esc_attr( $card['white'] ); ?>"></label></p><p><label>Beschreibung<br><input class="large-text" type="text" name="cards[<?php echo esc_attr( $index ); ?>][text]" value="<?php echo esc_attr( $card['text'] ); ?>"></label></p><p><label>Ziel-Link<br><input class="large-text" type="url" name="cards[<?php echo esc_attr( $index ); ?>][url]" value="<?php echo esc_attr( $card['url'] ); ?>" placeholder="https://… oder /seite/"></label></p></fieldset><?php endforeach; ?><p><button class="button button-primary" type="submit">Speichern</button></p></form></div><?php
}
function esc_river_rats_save_community_admin() {
	if ( ! current_user_can( 'edit_posts' ) || ! check_admin_referer( 'esc_save_community' ) ) { wp_die( 'Ungültige Anfrage.' ); }
	$defaults = esc_river_rats_community_defaults(); $cards = array(); $posted = isset( $_POST['cards'] ) && is_array( $_POST['cards'] ) ? wp_unslash( $_POST['cards'] ) : array();
	foreach ( $defaults['cards'] as $index => $default ) { $value = isset( $posted[ $index ] ) && is_array( $posted[ $index ] ) ? $posted[ $index ] : array(); $cards[] = array( 'yellow' => sanitize_text_field( $value['yellow'] ?? '' ), 'white' => sanitize_text_field( $value['white'] ?? '' ), 'text' => sanitize_text_field( $value['text'] ?? '' ), 'url' => esc_url_raw( $value['url'] ?? '' ) ); }
	update_option( 'esc_river_rats_community', array( 'eyebrow' => 'GEMEINSCHAFT', 'title' => sanitize_text_field( wp_unslash( $_POST['community_title'] ?? '' ) ), 'cards' => $cards ), false ); wp_safe_redirect( admin_url( 'admin.php?page=esc-community&saved=1' ) ); exit;
}
add_action( 'admin_post_esc_save_community', 'esc_river_rats_save_community_admin' );

/* ESC Header Builder: editorial data is synchronized to a native WordPress menu. */
function esc_river_rats_header_defaults() {
	return array(
		'logo_id' => (int) get_theme_mod( 'custom_logo', 0 ),
		'items' => array(
			array( 'key' => 'river-rats', 'label' => 'RIVER RATS', 'url' => '/river-rats/', 'parent' => '' ),
			array( 'key' => 'nachwuchs', 'label' => 'NACHWUCHS', 'url' => '/nachwuchs/', 'parent' => '' ),
			array( 'key' => 'u7', 'label' => 'U7', 'url' => '/nachwuchs/u7/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'u9', 'label' => 'U9', 'url' => '/nachwuchs/u9/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'u11', 'label' => 'U11', 'url' => '/nachwuchs/u11/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'u13', 'label' => 'U13', 'url' => '/nachwuchs/u13/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'u15', 'label' => 'U15', 'url' => '/nachwuchs/u15/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'u17', 'label' => 'U17', 'url' => '/nachwuchs/u17/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'u20', 'label' => 'U20', 'url' => '/nachwuchs/u20/', 'parent' => 'nachwuchs' ),
			array( 'key' => 'damen', 'label' => 'DAMEN', 'url' => '/damen/', 'parent' => '' ),
			array( 'key' => 'eiskunstlauf', 'label' => 'EISKUNSTLAUF', 'url' => '/eiskunstlauf/', 'parent' => '' ),
			array( 'key' => 'inklusion', 'label' => 'INKLUSIONSSPORT', 'url' => '/inklusion/', 'parent' => '' ),
			array( 'key' => 'eislaufschule', 'label' => 'EISLAUFSCHULE', 'url' => '/eislaufschule/', 'parent' => '' ),
			array( 'key' => 'verein', 'label' => 'VEREIN', 'url' => '/verein/', 'parent' => '' ),
			array( 'key' => 'foerderverein', 'label' => 'FÖRDERVEREIN', 'url' => '/foerderverein/', 'parent' => '' ),
			array( 'key' => 'news', 'label' => 'NEWS', 'url' => '/aktuelles/', 'parent' => '' ),
			array( 'key' => 'mitgliedschaft', 'label' => 'MITGLIED WERDEN', 'url' => '/mitgliedschaft/', 'parent' => '' ),
		),
	);
}
function esc_river_rats_get_header() {
	$saved = get_option( 'esc_river_rats_header', array() ); $defaults = esc_river_rats_header_defaults();
	return array( 'logo_id' => (int) ( $saved['logo_id'] ?? $defaults['logo_id'] ), 'items' => ! empty( $saved['items'] ) && is_array( $saved['items'] ) ? $saved['items'] : $defaults['items'] );
}
function esc_river_rats_sync_header_menu( $data = null ) {
	$data = $data ?: esc_river_rats_get_header(); $menu = wp_get_nav_menu_object( 'ESC Header' ); $menu_id = $menu ? (int) $menu->term_id : (int) wp_create_nav_menu( 'ESC Header' );
	if ( ! $menu_id ) { return 0; } $existing = wp_get_nav_menu_items( $menu_id ); foreach ( (array) $existing as $item ) { wp_delete_post( $item->ID, true ); }
	$ids = array();
	foreach ( $data['items'] as $item ) {
		$key = sanitize_key( $item['key'] ?? uniqid( 'menu-', false ) ); $parent = ! empty( $item['parent'] ) && isset( $ids[ sanitize_key( $item['parent'] ) ] ) ? $ids[ sanitize_key( $item['parent'] ) ] : 0;
		$created = wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => sanitize_text_field( $item['label'] ?? '' ), 'menu-item-url' => esc_url_raw( $item['url'] ?? '' ), 'menu-item-status' => 'publish', 'menu-item-parent-id' => $parent ) );
		if ( ! is_wp_error( $created ) ) { $ids[ $key ] = (int) $created; }
	}
	return $menu_id;
}
function esc_river_rats_ensure_header_defaults() {
	if ( false === get_option( 'esc_river_rats_header', false ) ) { $data = esc_river_rats_header_defaults(); add_option( 'esc_river_rats_header', $data, '', false ); esc_river_rats_sync_header_menu( $data ); }
}
add_action( 'after_switch_theme', 'esc_river_rats_ensure_header_defaults' ); add_action( 'init', 'esc_river_rats_ensure_header_defaults', 35 );
function esc_river_rats_render_header_navigation() {
	$menu = wp_get_nav_menu_object( 'ESC Header' ); if ( ! $menu ) { esc_river_rats_ensure_header_defaults(); $menu = wp_get_nav_menu_object( 'ESC Header' ); }
	return $menu ? '<button class="esc-mobile-menu-toggle" type="button" aria-expanded="false" aria-controls="esc-main-nav"><span></span><span></span><span></span><span class="screen-reader-text">Menü öffnen</span></button><nav id="esc-main-nav" class="esc-main-nav" aria-label="Hauptnavigation">' . wp_nav_menu( array( 'menu' => $menu->term_id, 'container' => false, 'echo' => false, 'fallback_cb' => false ) ) . '</nav>' : '';
}
function esc_river_rats_register_header_navigation_block() { register_block_type( get_theme_file_path( 'blocks/header-navigation' ), array( 'render_callback' => 'esc_river_rats_render_header_navigation' ) ); }
add_action( 'init', 'esc_river_rats_register_header_navigation_block' );
function esc_river_rats_header_admin_menu() { add_submenu_page( 'esc-community', 'Header', 'Header', 'edit_posts', 'esc-header', 'esc_river_rats_header_admin_page' ); }
add_action( 'admin_menu', 'esc_river_rats_header_admin_menu', 20 );
function esc_river_rats_header_admin_assets( $hook ) {
	if ( false === strpos( $hook, 'esc-header' ) ) { return; } wp_enqueue_media();
	wp_add_inline_script( 'media-editor', "document.addEventListener('DOMContentLoaded',function(){var b=document.querySelector('[data-esc-header-media]'),i=document.querySelector('[data-esc-header-logo-id]'),p=document.querySelector('[data-esc-header-logo-preview]');if(b){b.addEventListener('click',function(e){e.preventDefault();var f=wp.media({title:'Logo auswählen',button:{text:'Logo verwenden'},multiple:false});f.on('select',function(){var a=f.state().get('selection').first().toJSON();i.value=a.id;p.innerHTML='<img src=\\\"'+a.url+'\\\" alt=\\\"\\\" style=\\\"max-width:180px;max-height:80px;object-fit:contain\\\">';});f.open();});}document.addEventListener('click',function(e){var btn=e.target.closest('[data-esc-move]');if(!btn)return;var row=btn.closest('[data-esc-header-row]'),all=[...row.parentNode.children],n=all.indexOf(row)+(btn.dataset.escMove==='up'?-1:1);if(n>=0&&n<all.length){row.parentNode.insertBefore(row,all[n+(btn.dataset.escMove==='up'?0:1)]||null);}});});" );
}
add_action( 'admin_enqueue_scripts', 'esc_river_rats_header_admin_assets' );
function esc_river_rats_header_admin_page() {
	if ( ! current_user_can( 'edit_posts' ) ) { wp_die( 'Keine Berechtigung.' ); } $data = esc_river_rats_get_header(); $items = $data['items'];
	?><div class="wrap esc-header-admin"><h1>Header</h1><p>Logo und Navigation werden hier vereinfacht gepflegt. WordPress verwendet intern weiterhin das Standard-Navigationsmenü.</p><form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" style="max-width:980px"><input type="hidden" name="action" value="esc_save_header"><input type="hidden" name="_wp_http_referer" value="<?php echo esc_url( admin_url( 'admin.php?page=esc-header' ) ); ?>"><?php wp_nonce_field( 'esc_save_header' ); ?><fieldset style="margin:20px 0;padding:18px;background:#fff;border:1px solid #dcdcde"><legend><strong>Logo</strong></legend><button type="button" class="button" data-esc-header-media>Bild auswählen</button><input type="hidden" name="logo_id" data-esc-header-logo-id value="<?php echo esc_attr( $data['logo_id'] ); ?>"><span data-esc-header-logo-preview style="display:block;margin-top:12px"><?php echo $data['logo_id'] ? wp_get_attachment_image( $data['logo_id'], 'medium', false, array( 'style' => 'max-width:180px;max-height:80px;object-fit:contain' ) ) : ''; ?></span></fieldset><h2>Navigation</h2><p>Mit den Pfeilen die Reihenfolge ändern. Ein übergeordneter Punkt erzeugt ein Klappmenü.</p><div data-esc-header-items><?php foreach ( $items as $item ) : $key = sanitize_key( $item['key'] ?? uniqid( 'menu-', false ) ); ?><div data-esc-header-row style="display:grid;grid-template-columns:1fr 1.2fr 170px auto;gap:10px;align-items:end;margin:10px 0;padding:12px;background:#fff;border:1px solid #dcdcde"><input type="hidden" name="items[<?php echo esc_attr( $key ); ?>][key]" value="<?php echo esc_attr( $key ); ?>"><label>Bezeichnung<input class="large-text" type="text" name="items[<?php echo esc_attr( $key ); ?>][label]" value="<?php echo esc_attr( $item['label'] ?? '' ); ?>"></label><label>Link<input class="large-text" type="text" name="items[<?php echo esc_attr( $key ); ?>][url]" value="<?php echo esc_attr( $item['url'] ?? '' ); ?>"></label><label>Übergeordnet<select class="large-text" name="items[<?php echo esc_attr( $key ); ?>][parent]"><option value="">Hauptmenü</option><?php foreach ( $items as $parent ) : $parent_key = sanitize_key( $parent['key'] ?? '' ); if ( $parent_key === $key ) { continue; } ?><option value="<?php echo esc_attr( $parent_key ); ?>" <?php selected( $item['parent'] ?? '', $parent_key ); ?>><?php echo esc_html( $parent['label'] ?? '' ); ?></option><?php endforeach; ?></select></label><span><button type="button" class="button" data-esc-move="up" aria-label="Nach oben">↑</button> <button type="button" class="button" data-esc-move="down" aria-label="Nach unten">↓</button><label style="display:block;margin-top:7px"><input type="checkbox" name="items[<?php echo esc_attr( $key ); ?>][delete]" value="1"> löschen</label></span></div><?php endforeach; ?></div><p><button type="button" class="button" onclick="var c=document.querySelector('[data-esc-header-items]'),k='neu-'+Date.now(),d=document.createElement('div');d.setAttribute('data-esc-header-row','');d.style='display:grid;grid-template-columns:1fr 1.2fr 170px auto;gap:10px;align-items:end;margin:10px 0;padding:12px;background:#fff;border:1px solid #dcdcde';d.innerHTML='<input type=hidden name=items['+k+'][key] value='+k+'><label>Bezeichnung<input class=large-text name=items['+k+'][label]></label><label>Link<input class=large-text name=items['+k+'][url]></label><label>Übergeordnet<input class=large-text name=items['+k+'][parent] placeholder=optional></label><span><button type=button class=button data-esc-move=up>↑</button> <button type=button class=button data-esc-move=down>↓</button></span>';c.appendChild(d)">Menüpunkt hinzufügen</button></p><p><button class="button button-primary" type="submit">Speichern</button></p></form></div><?php
}
function esc_river_rats_save_header_admin() {
	if ( ! current_user_can( 'edit_posts' ) || ! check_admin_referer( 'esc_save_header' ) ) { wp_die( 'Ungültige Anfrage.' ); }
	$posted = isset( $_POST['items'] ) && is_array( $_POST['items'] ) ? wp_unslash( $_POST['items'] ) : array(); $items = array();
	foreach ( $posted as $key => $item ) { if ( ! is_array( $item ) || ! empty( $item['delete'] ) ) { continue; } $label = sanitize_text_field( $item['label'] ?? '' ); if ( ! $label ) { continue; } $items[] = array( 'key' => sanitize_key( $key ), 'label' => $label, 'url' => esc_url_raw( $item['url'] ?? '' ), 'parent' => sanitize_key( $item['parent'] ?? '' ) ); }
	$data = array( 'logo_id' => absint( $_POST['logo_id'] ?? 0 ), 'items' => $items ); update_option( 'esc_river_rats_header', $data, false ); if ( $data['logo_id'] ) { set_theme_mod( 'custom_logo', $data['logo_id'] ); } esc_river_rats_sync_header_menu( $data ); wp_safe_redirect( admin_url( 'admin.php?page=esc-header&saved=1' ) ); exit;
}
add_action( 'admin_post_esc_save_header', 'esc_river_rats_save_header_admin' );

/* Connects the native Query Loop to the six native category slugs. */
function esc_river_rats_query_loop_categories( $block ) {
    if ( 'core/query' !== ( $block['blockName'] ?? '' ) ) { return $block; }
    $namespace = $block['attrs']['namespace'] ?? '';
    if ( 0 !== strpos( $namespace, 'esc-news-' ) ) { return $block; }
    $slug = substr( $namespace, 9 );
    if ( 'area' === $slug ) {
        $current_slug = get_post_field( 'post_name', get_queried_object_id() );
        $area_map = array(
            'river-rats' => 'river-rats',
            'damen' => 'damen',
            'eiskunstlauf' => 'eiskunstlauf',
            'inklusion' => 'inklusion',
            'verein' => 'verein',
            'eislaufschule' => 'eislaufschule',
        );
        $slugs = isset( $area_map[ $current_slug ] ) ? array( $area_map[ $current_slug ] ) : array();
    } elseif ( 'team' === $slug || 'nachwuchs' === $slug ) {
        $current_slug = get_post_field( 'post_name', get_queried_object_id() );
        $team_slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20' );
        if ( in_array( $current_slug, $team_slugs, true ) ) {
            $slugs = array( $current_slug );
            $block['attrs']['query']['perPage'] = 6;
        } elseif ( in_array( $current_slug, array( 'river-rats', 'damen' ), true ) ) {
            $slugs = array( $current_slug );
            $block['attrs']['query']['perPage'] = 6;
        } elseif ( is_front_page() ) {
            $slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'eislaufschule' );
        } else {
            $slugs = array( 'nachwuchs' );
        }
    } elseif ( 'nachwuchs-all' === $slug ) {
        $slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'eislaufschule' );
    } else {
        $slugs = array( $slug );
    }
    if ( (int) ( $block['attrs']['query']['perPage'] ?? 0 ) > 1 ) { $block['attrs']['query']['perPage'] = 6; }
    $term_ids = array();
    foreach ( $slugs as $term_slug ) {
        $term = get_term_by( 'slug', $term_slug, 'category' );
        if ( $term && ! is_wp_error( $term ) ) { $term_ids[] = (int) $term->term_id; }
    }
    if ( $term_ids ) {
        $block['attrs']['query']['taxQuery'] = array( 'include' => array( 'category' => $term_ids ) );
    }
    return $block;
}
add_filter( 'render_block_data', 'esc_river_rats_query_loop_categories' );

/* Enforce the same category restriction on the final Query Loop arguments. */
function esc_river_rats_query_loop_vars( $query, $block ) {
    if ( ! is_object( $block ) || 'core/query' !== ( $block->name ?? '' ) ) { return $query; }
    $namespace = $block->parsed_block['attrs']['namespace'] ?? '';
    if ( 0 !== strpos( $namespace, 'esc-news-' ) ) { return $query; }
    $slug = substr( $namespace, 9 );
    if ( 'area' === $slug ) {
        $current_slug = get_post_field( 'post_name', get_queried_object_id() );
        $slugs = in_array( $current_slug, array( 'river-rats', 'damen', 'eiskunstlauf', 'inklusion', 'verein', 'eislaufschule' ), true ) ? array( $current_slug ) : array();
    } elseif ( 'nachwuchs' === $slug || 'team' === $slug ) {
        $current_slug = get_post_field( 'post_name', get_queried_object_id() );
        $team_slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20' );
        if ( in_array( $current_slug, $team_slugs, true ) || in_array( $current_slug, array( 'river-rats', 'damen' ), true ) ) {
            $slugs = array( $current_slug );
        } elseif ( is_front_page() ) {
            $slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'eislaufschule' );
        } else {
            $slugs = array( 'nachwuchs' );
        }
    } elseif ( 'nachwuchs-all' === $slug ) {
        $slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'eislaufschule' );
    } else {
        $slugs = array( $slug );
    }
    $term_ids = array();
    foreach ( $slugs as $term_slug ) {
        $term = get_term_by( 'slug', $term_slug, 'category' );
        if ( $term && ! is_wp_error( $term ) ) { $term_ids[] = (int) $term->term_id; }
    }
    if ( $term_ids ) {
        $query['category__in'] = $term_ids;
        $query['tax_query'] = array(
            array(
                'taxonomy' => 'category',
                'field'    => 'term_id',
                'terms'    => $term_ids,
                'operator' => 'IN',
            ),
        );
    }
    return $query;
}
add_filter( 'query_loop_block_query_vars', 'esc_river_rats_query_loop_vars', 10, 2 );

/* Filter the central News blog with standard WordPress query parameters. */
function esc_river_rats_blog_query_vars( $query, $block ) {
    if ( ! is_object( $block ) || 'core/query' !== ( $block->name ?? '' ) ) { return $query; }
    $namespace = $block->parsed_block['attrs']['namespace'] ?? '';
    if ( ! in_array( $namespace, array( 'esc-news-blog', 'esc-news-category' ), true ) ) { return $query; }
    if ( ! empty( $_GET['news_search'] ) ) {
        $query['s'] = sanitize_text_field( wp_unslash( $_GET['news_search'] ) );
    }
    if ( 'esc-news-category' === $namespace && is_category() ) {
        $term = get_queried_object();
        if ( $term && ! empty( $term->term_id ) ) { $query['category__in'] = array( (int) $term->term_id ); }
    } elseif ( ! empty( $_GET['news_category'] ) && 'alle' !== $_GET['news_category'] ) {
        $term = get_term_by( 'slug', sanitize_title( wp_unslash( $_GET['news_category'] ) ), 'category' );
        if ( $term && ! is_wp_error( $term ) ) { $query['category__in'] = array( (int) $term->term_id ); }
    }
    if ( ! empty( $_GET['news_year'] ) && preg_match( '/^20[0-9]{2}$/', $_GET['news_year'] ) ) {
        $query['year'] = absint( $_GET['news_year'] );
    }
    $flashnews = get_term_by( 'slug', 'flashnews', 'category' );
    if ( $flashnews && ! is_wp_error( $flashnews ) ) {
        $query['category__not_in'] = array( (int) $flashnews->term_id );
    }
    return $query;
}
add_filter( 'query_loop_block_query_vars', 'esc_river_rats_blog_query_vars', 10, 2 );

/* Render the News controls server-side so years and categories stay current. */
function esc_river_rats_render_news_filters() {
    $categories = esc_river_rats_news_categories();
    $flashnews = get_term_by( 'slug', 'flashnews', 'category' );
    $year_query = array( 'post_type' => 'post', 'post_status' => 'publish', 'posts_per_page' => -1, 'fields' => 'ids', 'date_query' => array( array( 'after' => '2000-01-01' ) ) );
    if ( $flashnews && ! is_wp_error( $flashnews ) ) { $year_query['category__not_in'] = array( (int) $flashnews->term_id ); }
    $years = get_posts( $year_query );
    $year_values = array();
    foreach ( $years as $post_id ) { $year_values[] = (int) get_post_time( 'Y', false, $post_id ); }
    $year_values = array_values( array_unique( $year_values ) );
    rsort( $year_values );
    $is_category_archive = is_category();
    $selected_category = isset( $_GET['news_category'] ) ? sanitize_title( wp_unslash( $_GET['news_category'] ) ) : 'alle';
    $selected_year = isset( $_GET['news_year'] ) ? absint( $_GET['news_year'] ) : 0;
    $search = isset( $_GET['news_search'] ) ? sanitize_text_field( wp_unslash( $_GET['news_search'] ) ) : '';
    ob_start();
    ?>
    <nav class="news-blog-filters<?php echo $is_category_archive ? ' news-blog-filters--category' : ''; ?>" aria-label="News filtern">
        <?php if ( ! $is_category_archive ) : ?><div class="news-blog-tabs">
            <a class="<?php echo 'alle' === $selected_category ? 'is-active' : ''; ?>" href="<?php echo esc_url( remove_query_arg( array( 'news_category', 'news_year', 'news_search', 'paged' ) ) ); ?>">Alle News</a>
            <?php foreach ( $categories as $slug => $name ) : ?>
                <?php if ( in_array( $slug, array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'flashnews' ), true ) ) { continue; } ?>
                <a class="<?php echo esc_attr( $slug === $selected_category ? 'is-active' : '' ); ?>" href="<?php echo esc_url( add_query_arg( array( 'news_category' => $slug, 'paged' => false ) ) ); ?>"><?php echo esc_html( $name ); ?></a>
            <?php endforeach; ?>
        </div><?php endif; ?>
        <form method="get" class="news-blog-form">
            <label><span class="screen-reader-text">News durchsuchen</span><input type="search" name="news_search" value="<?php echo esc_attr( $search ); ?>" placeholder="News durchsuchen …"></label>
            <?php if ( ! $is_category_archive ) : ?><label><span class="screen-reader-text">Kategorie auswählen</span><select name="news_category"><option value="alle">Alle Kategorien</option><?php foreach ( $categories as $slug => $name ) : if ( in_array( $slug, array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'flashnews' ), true ) ) { continue; } ?><option value="<?php echo esc_attr( $slug ); ?>" <?php selected( $selected_category, $slug ); ?>><?php echo esc_html( $name ); ?></option><?php endforeach; ?></select></label><?php endif; ?>
            <label><span class="screen-reader-text">Jahr auswählen</span><select name="news_year"><option value="0">Alle Jahre</option><?php foreach ( $year_values as $year ) : ?><option value="<?php echo esc_attr( $year ); ?>" <?php selected( $selected_year, $year ); ?>><?php echo esc_html( $year ); ?></option><?php endforeach; ?></select></label>
            <button type="submit">Filtern</button>
        </form>
    </nav>
    <?php
    return ob_get_clean();
}

function esc_river_rats_register_news_filters_block() {
    register_block_type( 'esc-river-rats/news-filters', array( 'render_callback' => 'esc_river_rats_render_news_filters' ) );
}
add_action( 'init', 'esc_river_rats_register_news_filters_block' );

/* Bind the category filter at render time, when the Query Loop context is known. */
function esc_river_rats_bind_news_query( $pre_render, $parsed_block ) {
    if ( 'core/query' !== ( $parsed_block['blockName'] ?? '' ) ) { return $pre_render; }
    $namespace = $parsed_block['attrs']['namespace'] ?? '';
    if ( 0 !== strpos( $namespace, 'esc-news-' ) ) { return $pre_render; }
    $slug = substr( $namespace, 9 );
    if ( in_array( $slug, array( 'verein', 'river-rats', 'damen', 'eiskunstlauf', 'inklusion', 'eislaufschule' ), true ) ) {
        $slugs = array( $slug );
    } elseif ( 'nachwuchs' === $slug || 'nachwuchs-all' === $slug ) {
        $slugs = array( 'nachwuchs' );
        if ( is_front_page() || 'nachwuchs-all' === $slug ) { $slugs = array( 'u7', 'u9', 'u11', 'u13', 'u15', 'u17', 'u20', 'eislaufschule' ); }
    } elseif ( 'area' === $slug ) {
        $current = get_post_field( 'post_name', get_queried_object_id() );
        $slugs = in_array( $current, array( 'river-rats', 'damen', 'eiskunstlauf', 'inklusion', 'verein', 'eislaufschule' ), true ) ? array( $current ) : array();
    } else { $slugs = array( $slug ); }
    $ids = array();
    foreach ( $slugs as $term_slug ) {
        $term = get_term_by( 'slug', $term_slug, 'category' );
        if ( $term && ! is_wp_error( $term ) ) { $ids[] = (int) $term->term_id; }
    }
    if ( ! $ids ) { return $pre_render; }
    $query_filter = null;
    $query_filter = function ( $query ) use ( &$query_filter, $ids ) {
        remove_filter( 'query_loop_block_query_vars', $query_filter, 10 );
        $query['category__in'] = $ids;
        $query['tax_query'] = array(
            array(
                'taxonomy' => 'category',
                'field'    => 'term_id',
                'terms'    => $ids,
                'operator' => 'IN',
            ),
        );
        return $query;
    };
    add_filter( 'query_loop_block_query_vars', $query_filter, 10, 1 );
    return $pre_render;
}
add_filter( 'pre_render_block', 'esc_river_rats_bind_news_query', 10, 2 );

function esc_river_rats_bind_blog_query( $pre_render, $parsed_block ) {
    $namespace = $parsed_block['attrs']['namespace'] ?? '';
    if ( 'core/query' !== ( $parsed_block['blockName'] ?? '' ) || ! in_array( $namespace, array( 'esc-news-blog', 'esc-news-category' ), true ) ) { return $pre_render; }
    $query_filter = null;
    $query_filter = function ( $query ) use ( &$query_filter, $namespace ) {
        if ( ! empty( $_GET['news_search'] ) ) { $query['s'] = sanitize_text_field( wp_unslash( $_GET['news_search'] ) ); }
        if ( 'esc-news-category' === $namespace && is_category() ) {
            $term = get_queried_object();
            if ( $term && ! empty( $term->term_id ) ) { $query['category__in'] = array( (int) $term->term_id ); }
        } elseif ( ! empty( $_GET['news_category'] ) && 'alle' !== $_GET['news_category'] ) {
            $term = get_term_by( 'slug', sanitize_title( wp_unslash( $_GET['news_category'] ) ), 'category' );
            if ( $term && ! is_wp_error( $term ) ) { $query['category__in'] = array( (int) $term->term_id ); }
        }
        if ( ! empty( $_GET['news_year'] ) && preg_match( '/^20[0-9]{2}$/', $_GET['news_year'] ) ) { $query['year'] = absint( $_GET['news_year'] ); }
        $flashnews = get_term_by( 'slug', 'flashnews', 'category' );
        if ( $flashnews && ! is_wp_error( $flashnews ) ) { $query['category__not_in'] = array( (int) $flashnews->term_id ); }
        remove_filter( 'query_loop_block_query_vars', $query_filter, 10 );
        return $query;
    };
    add_filter( 'query_loop_block_query_vars', $query_filter, 10, 1 );
    return $pre_render;
}
add_filter( 'pre_render_block', 'esc_river_rats_bind_blog_query', 11, 2 );

/* Add consistent date and category metadata below every native post teaser. */
function esc_river_rats_news_excerpt_meta( $content, $block ) {
    if ( 'core/post-excerpt' !== ( $block['blockName'] ?? '' ) || 'post' !== get_post_type() ) { return $content; }
    if ( is_page( 'aktuelles' ) ) { return $content; }
    $categories = get_the_category();
    $category = $categories ? esc_html( $categories[0]->name ) : '';
    $meta = '<div class="news-meta"><time datetime="' . esc_attr( get_the_date( 'c' ) ) . '">' . esc_html( get_the_date() ) . '</time>';
    if ( $category ) { $meta .= '<span>' . $category . '</span>'; }
    return $meta . '</div>' . $content;
}
add_filter( 'render_block', 'esc_river_rats_news_excerpt_meta', 20, 2 );

/* The public theme is intentionally publication-only: no comment UI or intake. */
function esc_river_rats_disable_public_comments( $open ) { return false; }
add_filter( 'comments_open', 'esc_river_rats_disable_public_comments', 20 );
add_filter( 'pings_open', 'esc_river_rats_disable_public_comments', 20 );
function esc_river_rats_hide_comment_blocks( $block_content, $block ) {
    return 'core/comments' === ( $block['blockName'] ?? '' ) ? '' : $block_content;
}
add_filter( 'render_block', 'esc_river_rats_hide_comment_blocks', 20, 2 );

function esc_river_rats_assets() {
    wp_enqueue_style( 'esc-river-rats', get_stylesheet_uri(), array(), '1.72.0' );
    wp_enqueue_script( 'esc-river-rats-header', get_theme_file_uri( 'assets/header-menu.js' ), array(), '1.72.0', true );
    wp_enqueue_script( 'esc-river-rats-next-home-game', get_theme_file_uri( 'assets/next-home-game.js' ), array(), '1.72.0', true );
}
add_action( 'wp_enqueue_scripts', 'esc_river_rats_assets' );

function esc_river_rats_image( $file ) {
    return esc_url( get_theme_file_uri( 'assets/images/' . ltrim( $file, '/' ) ) );
}
