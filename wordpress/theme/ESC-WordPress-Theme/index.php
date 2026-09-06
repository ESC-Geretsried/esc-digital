<?php
/**
 * Classic fallback. WordPress block themes render through templates/index.html.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
?><!doctype html><html <?php language_attributes(); ?>><head><meta charset="<?php bloginfo( 'charset' ); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><title><?php bloginfo( 'name' ); ?></title><?php wp_head(); ?></head><body <?php body_class(); ?>><?php wp_body_open(); ?><main><?php if ( have_posts() ) : while ( have_posts() ) : the_post(); the_content(); endwhile; endif; ?></main><?php wp_footer(); ?></body></html>
