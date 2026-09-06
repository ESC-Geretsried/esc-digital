<?php
/**
 * Title: Bereichsseite mit News
 * Slug: esc-river-rats/area-content
 * Categories: esc-river-rats
 */
?>
<!-- wp:group {"className":"section shell area-content","layout":{"type":"constrained"}} --><main class="wp-block-group section shell area-content"><!-- wp:post-title {"level":1} /--><!-- wp:post-content /--><div class="section-heading"><h2>AKTUELLES</h2></div><!-- wp:query {"namespace":"esc-news-area","query":{"perPage":6,"postType":"post","inherit":false}} --><div class="wp-block-query cards cards-3"><!-- wp:post-template --><!-- wp:group {"className":"card news-archive-card"} --><article class="wp-block-group card news-archive-card"><!-- wp:post-featured-image {"isLink":true} /--><!-- wp:post-title {"isLink":true,"level":3} /--><!-- wp:post-date /--><!-- wp:post-excerpt /--></article><!-- /wp:group --><!-- /wp:post-template --><!-- wp:query-no-results --><p>Noch keine freigegebenen Meldungen.</p><!-- /wp:query-no-results --></div><!-- /wp:query --><p class="news-card__all"><a href="/aktuelles/">ALLE NEWS</a></p></main><!-- /wp:group -->
