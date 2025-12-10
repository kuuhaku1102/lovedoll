<?php
/**
 * The template for displaying all single dolls
 */

get_header();
?>

<main id="primary" class="site-main">

    <?php
    while ( have_posts() ) :
        the_post();
        ?>

        <article id="post-<?php the_ID(); ?>" <?php post_class('doll-review-article'); ?>>
            
            <header class="entry-header container section-padding text-center">
                <?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
                <div class="doll-meta">
                    <!-- Example Meta Data -->
                    <span class="meta-item">Height: 160cm</span> | 
                    <span class="meta-item">Material: Silicone</span>
                </div>
            </header>

            <div class="container entry-content">
                
                <div class="doll-featured-image text-center mb-4">
                    <?php the_post_thumbnail('large'); ?>
                </div>

                <!-- Review Section: Merits & Demerits -->
                <div class="review-grid grid-2">
                    <div class="card merit-card">
                        <h3 class="text-gold">Merits</h3>
                        <ul>
                            <li>Extremely realistic skin texture</li>
                            <li>High range of motion in joints</li>
                            <li>Easy to clean face attachment</li>
                        </ul>
                    </div>
                    <div class="card demerit-card">
                        <h3>Demerits</h3>
                        <ul>
                            <li>Heavy weight (35kg) makes moving difficult</li>
                            <li>Higher price point</li>
                        </ul>
                    </div>
                </div>

                <div class="content-body section-padding">
                    <?php the_content(); ?>
                </div>

                <!-- Affiliate CTA -->
                <div class="affiliate-cta text-center section-padding bg-light">
                    <h3>Interested in this model?</h3>
                    <p>Get the best price with anonymous delivery.</p>
                    <a href="#" class="btn btn-primary btn-lg">Check Lowest Price & Availability</a>
                </div>

            </div>

        </article>

    <?php
    endwhile; // End of the loop.
    ?>

</main><!-- #main -->

<?php
get_footer();
