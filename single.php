<?php
/**
 * The template for displaying all single posts
 */

get_header();
?>

<main id="primary" class="site-main container section-padding">

    <?php
    while ( have_posts() ) :
        the_post();
        ?>

        <article id="post-<?php the_ID(); ?>" <?php post_class('single-post-article'); ?>>
            
            <header class="entry-header text-center mb-5">
                <div class="entry-meta mb-3">
                    <span class="posted-on"><?php echo get_the_date('Y.m.d'); ?></span>
                    <?php
                    $categories = get_the_category();
                    if ( ! empty( $categories ) ) {
                        echo '<span class="cat-separator">|</span>';
                        foreach ( $categories as $category ) {
                            echo '<a href="' . esc_url( get_category_link( $category->term_id ) ) . '" class="cat-link">' . esc_html( $category->name ) . '</a> ';
                        }
                    }
                    ?>
                </div>
                
                <h1 class="entry-title mb-4"><?php the_title(); ?></h1>

                <?php if ( has_post_thumbnail() ) : ?>
                    <div class="entry-thumbnail mb-4">
                        <?php the_post_thumbnail('large'); ?>
                    </div>
                <?php endif; ?>
            </header>

            <div class="entry-content">
                <?php
                the_content();

                wp_link_pages(
                    array(
                        'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'lovedoll' ),
                        'after'  => '</div>',
                    )
                );
                ?>
            </div>

            <footer class="entry-footer mt-5">
                <div class="post-tags">
                    <?php the_tags( '<span class="tags-label">Tags:</span> ', ', ', '' ); ?>
                </div>

                <div class="post-navigation mt-5">
                    <div class="nav-links d-flex justify-content-between">
                        <div class="nav-previous"><?php previous_post_link( '%link', '&laquo; %title' ); ?></div>
                        <div class="nav-next"><?php next_post_link( '%link', '%title &raquo;' ); ?></div>
                    </div>
                </div>
            </footer>
            
        </article>

        <?php
        // If comments are open or we have at least one comment, load up the comment template.
        if ( comments_open() || get_comments_number() ) :
            comments_template();
        endif;

    endwhile; // End of the loop.
    ?>

</main><!-- #main -->

<?php
get_footer();
