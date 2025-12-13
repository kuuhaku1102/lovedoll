	<footer id="colophon" class="site-footer">
		<div class="footer-content">
			<div class="container">
				<div class="footer-grid">
					<!-- About Section -->
					<div class="footer-column">
						<h3 class="footer-heading">About</h3>
						<p class="footer-description">
							<?php bloginfo('name'); ?>は、ラブドールの最安値比較・ランキング情報を提供する専門サイトです。初心者の方でも安心して選べるよう、信頼できる情報をお届けします。
						</p>
						<div class="footer-social">
							<!-- Social icons can be added here -->
						</div>
					</div>
					
					<!-- Quick Links -->
					<div class="footer-column">
						<h3 class="footer-heading">Quick Links</h3>
						<ul class="footer-menu">
							<li><a href="<?php echo home_url('/'); ?>">ホーム</a></li>
							<li><a href="<?php echo home_url('/#ranking'); ?>">ランキング</a></li>
							<li><a href="<?php echo home_url('/#guide'); ?>">選び方ガイド</a></li>
							<li><a href="<?php echo home_url('/#blog'); ?>">コラム記事</a></li>
						</ul>
					</div>
					
					<!-- Categories -->
					<div class="footer-column">
						<h3 class="footer-heading">Categories</h3>
						<ul class="footer-menu">
							<?php
							$categories = get_categories(array(
								'orderby' => 'count',
								'order' => 'DESC',
								'number' => 5
							));
							foreach ($categories as $category) {
								echo '<li><a href="' . get_category_link($category->term_id) . '">' . $category->name . '</a></li>';
							}
							?>
						</ul>
					</div>
					
					<!-- Recent Posts -->
					<div class="footer-column">
						<h3 class="footer-heading">Recent Posts</h3>
						<ul class="footer-menu footer-posts">
							<?php
							$recent_posts = wp_get_recent_posts(array(
								'numberposts' => 5,
								'post_status' => 'publish'
							));
							foreach ($recent_posts as $recent) {
								echo '<li><a href="' . get_permalink($recent['ID']) . '">' . $recent['post_title'] . '</a></li>';
							}
							wp_reset_query();
							?>
						</ul>
					</div>
				</div>
				
				<!-- Footer Bottom -->
				<div class="footer-bottom">
					<div class="footer-bottom-content">
						<p class="copyright">
							&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.
						</p>
						<ul class="footer-legal">
							<li><a href="<?php echo home_url('/privacy-policy/'); ?>">プライバシーポリシー</a></li>
							<li><a href="<?php echo home_url('/terms/'); ?>">利用規約</a></li>
							<li><a href="<?php echo home_url('/contact/'); ?>">お問い合わせ</a></li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</footer><!-- #colophon -->
</div><!-- #page -->

<?php wp_footer(); ?>

</body>
</html>
