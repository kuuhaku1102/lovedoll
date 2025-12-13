<?php
/**
 * The template for displaying the blog index (posts page)
 */

get_header();
?>

<main id="primary" class="site-main container section-padding">

    <header class="page-header mb-5 text-center">
        <h1 class="page-title section-title">📝 コラム</h1>
        <p class="section-desc">ラブドールに関する役立つ情報をお届けします</p>
    </header>

    <?php if ( have_posts() ) : ?>
        <div class="blog-list-grid">
            <?php
            while ( have_posts() ) :
                the_post();
                ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class('blog-list-card'); ?>>
                    <div class="blog-list-content">
                        <div class="blog-list-meta">
                            <span class="blog-list-date"><?php echo get_the_date('Y.m.d'); ?></span>
                            <?php
                            $categories = get_the_category();
                            if (!empty($categories)) {
                                echo '<span class="blog-list-category">' . esc_html($categories[0]->name) . '</span>';
                            }
                            ?>
                        </div>
                        <h2 class="blog-list-title">
                            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                        </h2>
                        <div class="blog-list-excerpt">
                            <?php echo wp_trim_words(get_the_excerpt(), 50, '...'); ?>
                        </div>
                        <div class="blog-list-footer">
                            <a href="<?php the_permalink(); ?>" class="blog-list-read-more">続きを読む →</a>
                            <?php
                            $tags = get_the_tags();
                            if ($tags) {
                                echo '<div class="blog-list-tags">';
                                $tag_count = 0;
                                foreach ($tags as $tag) {
                                    if ($tag_count >= 3) break;
                                    echo '<span class="tag-item">#' . esc_html($tag->name) . '</span>';
                                    $tag_count++;
                                }
                                echo '</div>';
                            }
                            ?>
                        </div>
                    </div>
                </article>
                <?php
            endwhile;
            ?>
        </div>
        
        <div class="pagination">
            <?php 
            the_posts_pagination( array(
                'mid_size'  => 2,
                'prev_text' => '&laquo; 前へ',
                'next_text' => '次へ &raquo;',
            ) ); 
            ?>
        </div>

    <?php else : ?>
        <div class="no-results text-center">
            <p>記事が見つかりませんでした。</p>
        </div>
    <?php endif; ?>

</main><!-- #main -->

<?php
get_footer();
