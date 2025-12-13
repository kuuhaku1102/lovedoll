<?php
/**
 * WordPress ページ作成スクリプト
 * 
 * 使い方：
 * wp-admin にログイン後、以下のURLにアクセス
 * https://yourdomain.com/wp-content/themes/your-theme/create-pages.php
 * 
 * または、wp-cli を使用：
 * wp eval-file create-pages.php
 */

// WordPress 環境をロード
require_once('../../../wp-load.php');

// 管理者権限チェック
if (!current_user_can('manage_options')) {
    die('このスクリプトは管理者のみ実行できます。');
}

// 作成するページの定義
$pages = array(
    array(
        'post_title'    => '用途別おすすめ',
        'post_name'     => 'purpose-based',
        'post_content'  => '',
        'post_status'   => 'publish',
        'post_type'     => 'page',
        'post_author'   => 1,
        'page_template' => 'page-purpose-based.php',
        'meta_input'    => array(
            '_wp_page_template' => 'page-purpose-based.php'
        )
    ),
    array(
        'post_title'    => 'キャンペーン情報',
        'post_name'     => 'campaigns',
        'post_content'  => '',
        'post_status'   => 'publish',
        'post_type'     => 'page',
        'post_author'   => 1,
        'page_template' => 'page-campaigns.php',
        'meta_input'    => array(
            '_wp_page_template' => 'page-campaigns.php'
        )
    ),
    array(
        'post_title'    => '販売店比較',
        'post_name'     => 'shop-comparison',
        'post_content'  => '',
        'post_status'   => 'publish',
        'post_type'     => 'page',
        'post_author'   => 1,
        'page_template' => 'page-shop-comparison.php',
        'meta_input'    => array(
            '_wp_page_template' => 'page-shop-comparison.php'
        )
    )
);

echo '<h1>WordPress ページ作成スクリプト</h1>';
echo '<p>以下のページを作成します...</p>';
echo '<ul>';

foreach ($pages as $page) {
    // 既存ページをチェック
    $existing_page = get_page_by_path($page['post_name']);
    
    if ($existing_page) {
        echo '<li><strong>' . esc_html($page['post_title']) . '</strong>: すでに存在します（ID: ' . $existing_page->ID . '）</li>';
        
        // テンプレートを更新
        update_post_meta($existing_page->ID, '_wp_page_template', $page['page_template']);
        echo '<ul><li>テンプレートを更新しました: ' . esc_html($page['page_template']) . '</li></ul>';
    } else {
        // ページを作成
        $page_id = wp_insert_post($page);
        
        if ($page_id && !is_wp_error($page_id)) {
            echo '<li><strong>' . esc_html($page['post_title']) . '</strong>: 作成成功（ID: ' . $page_id . '）</li>';
            echo '<ul>';
            echo '<li>URL: ' . get_permalink($page_id) . '</li>';
            echo '<li>テンプレート: ' . esc_html($page['page_template']) . '</li>';
            echo '</ul>';
        } else {
            echo '<li><strong>' . esc_html($page['post_title']) . '</strong>: 作成失敗</li>';
            if (is_wp_error($page_id)) {
                echo '<ul><li>エラー: ' . $page_id->get_error_message() . '</li></ul>';
            }
        }
    }
}

echo '</ul>';
echo '<hr>';
echo '<h2>作成されたページ一覧</h2>';
echo '<ul>';

// 作成されたページのリンクを表示
foreach ($pages as $page) {
    $created_page = get_page_by_path($page['post_name']);
    if ($created_page) {
        echo '<li><a href="' . get_permalink($created_page->ID) . '" target="_blank">' . esc_html($page['post_title']) . '</a></li>';
    }
}

echo '</ul>';
echo '<hr>';
echo '<p><strong>完了しました！</strong></p>';
echo '<p><a href="' . admin_url() . '">管理画面に戻る</a></p>';
