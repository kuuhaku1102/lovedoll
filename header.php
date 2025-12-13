<!doctype html>
<html <?php language_attributes(); ?>>
<head>
		<!-- Matomo -->
<script>
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="//matomo.sakura.ne.jp/matomo/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '10']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
</script>
<!-- End Matomo Code -->
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="profile" href="https://gmpg.org/xfn/11">
	
	<!-- SEO Meta Tags -->
	<?php
	$page_title = wp_get_document_title();
	$page_description = '';
	$page_keywords = '';
	$page_url = get_permalink();
	$site_name = get_bloginfo('name');
	$og_image = get_template_directory_uri() . '/images/og-default.jpg';
	
	if (is_singular()) {
		if (has_excerpt()) {
			$page_description = get_the_excerpt();
		} else {
			$page_description = wp_trim_words(get_the_content(), 30, '...');
		}
		
		// Get tags as keywords
		$tags = get_the_tags();
		if ($tags) {
			$tag_names = array();
			foreach ($tags as $tag) {
				$tag_names[] = $tag->name;
			}
			$page_keywords = implode(', ', $tag_names);
		}
		
		if (has_post_thumbnail()) {
			$og_image = get_the_post_thumbnail_url(get_the_ID(), 'full');
		}
	} elseif (is_home() || is_front_page()) {
		$page_description = 'ラブドール最安値比較サイト。国内正規品のラブドールを価格・品質・保証で徹底比較。初心者向けガイド、人気ランキング、匿名配送対応ショップ情報を掲載。';
		$page_keywords = 'ラブドール, 最安値, 比較, ランキング, 国内正規品, 匿名配送, 初心者ガイド';
	} elseif (is_category()) {
		$page_description = category_description();
	} elseif (is_tag()) {
		$page_description = tag_description();
	}
	
	$page_description = strip_tags($page_description);
	$page_description = str_replace('"', '&quot;', $page_description);
	?>
	
	<?php if ($page_description): ?>
	<meta name="description" content="<?php echo esc_attr($page_description); ?>">
	<?php endif; ?>
	
	<?php if ($page_keywords): ?>
	<meta name="keywords" content="<?php echo esc_attr($page_keywords); ?>">
	<?php endif; ?>
	
	<!-- Open Graph Tags -->
	<meta property="og:type" content="<?php echo is_singular() ? 'article' : 'website'; ?>">
	<meta property="og:title" content="<?php echo esc_attr($page_title); ?>">
	<meta property="og:description" content="<?php echo esc_attr($page_description); ?>">
	<meta property="og:url" content="<?php echo esc_url($page_url); ?>">
	<meta property="og:site_name" content="<?php echo esc_attr($site_name); ?>">
	<meta property="og:image" content="<?php echo esc_url($og_image); ?>">
	<meta property="og:locale" content="ja_JP">
	
	<!-- Twitter Card Tags -->
	<meta name="twitter:card" content="summary_large_image">
	<meta name="twitter:title" content="<?php echo esc_attr($page_title); ?>">
	<meta name="twitter:description" content="<?php echo esc_attr($page_description); ?>">
	<meta name="twitter:image" content="<?php echo esc_url($og_image); ?>">
	
	<!-- Canonical URL -->
	<link rel="canonical" href="<?php echo esc_url($page_url); ?>">

	<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
	<a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e( 'Skip to content', 'lovedoll-premium' ); ?></a>

	<header id="masthead" class="site-header">
		<div class="site-branding">
			<?php
			if ( has_custom_logo() ) {
				the_custom_logo();
			} else {
                ?>
                <h1 class="site-title"><a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home"><?php bloginfo( 'name' ); ?></a></h1>
                <?php
            }
			
            $lovedoll_description = get_bloginfo( 'description', 'display' );
			if ( $lovedoll_description || is_customize_preview() ) :
				?>
				<p class="site-description"><?php echo $lovedoll_description; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></p>
			<?php endif; ?>
		</div><!-- .site-branding -->

		<nav id="site-navigation" class="main-navigation">
			<button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
				<span class="screen-reader-text"><?php esc_html_e( 'Primary Menu', 'lovedoll-premium' ); ?></span>
                <span class="hamburger-box">
                    <span class="hamburger-inner"></span>
                </span>
			</button>
            <div class="menu-container">
                <?php
                wp_nav_menu(
                    array(
                        'theme_location' => 'primary',
                        'menu_id'        => 'primary-menu',
                        'container'      => false,
                    )
                );
                ?>
            </div>
		</nav><!-- #site-navigation -->
	</header><!-- #masthead -->
