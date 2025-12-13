<?php
/**
 * アフィリエイトリンク管理画面
 */

// 直接アクセスを防止
if (!defined('ABSPATH')) {
    exit;
}

// 管理画面メニューに追加
add_action('admin_menu', 'lovedoll_affiliate_links_menu');

function lovedoll_affiliate_links_menu() {
    add_menu_page(
        'アフィリエイトリンク管理',
        'アフィリエイトリンク',
        'manage_options',
        'lovedoll-affiliate-links',
        'lovedoll_affiliate_links_page',
        'dashicons-admin-links',
        30
    );
}

// 管理画面ページの表示
function lovedoll_affiliate_links_page() {
    // 設定を取得
    $affiliate_links = get_option('lovedoll_affiliate_links', array());
    ?>
    <div class="wrap">
        <h1>
            <span class="dashicons dashicons-admin-links" style="font-size: 32px; margin-right: 10px;"></span>
            アフィリエイトリンク管理
        </h1>
        <p>プラグインが出力したリンクを自動的にアフィリエイトリンクに変換します。</p>
        
        <div id="affiliate-links-app">
            <div class="notice notice-info">
                <p><strong>💡 使い方</strong></p>
                <ul>
                    <li>サイトのドメイン（例：<code>yourdoll.jp</code>）を入力</li>
                    <li>アフィリエイトパラメータ（例：<code>?ref=kuuhaku-lovedoll</code>）を入力</li>
                    <li>「有効」にチェックを入れて保存</li>
                    <li>ページ内のすべてのリンクが自動的に変換されます</li>
                </ul>
            </div>

            <div class="card" style="max-width: 100%; margin-top: 20px;">
                <h2>アフィリエイトリンク設定</h2>
                
                <table class="wp-list-table widefat fixed striped" id="affiliate-links-table">
                    <thead>
                        <tr>
                            <th style="width: 5%;">有効</th>
                            <th style="width: 20%;">サイト名</th>
                            <th style="width: 25%;">ドメイン</th>
                            <th style="width: 30%;">アフィリエイトパラメータ</th>
                            <th style="width: 15%;">プレビュー</th>
                            <th style="width: 5%;">操作</th>
                        </tr>
                    </thead>
                    <tbody id="affiliate-links-tbody">
                        <!-- JavaScript で動的に追加 -->
                    </tbody>
                </table>

                <div style="margin-top: 20px;">
                    <button type="button" class="button button-secondary" id="add-affiliate-link">
                        <span class="dashicons dashicons-plus-alt" style="vertical-align: middle;"></span>
                        新しいサイトを追加
                    </button>
                    <button type="button" class="button button-primary" id="save-affiliate-links" style="margin-left: 10px;">
                        <span class="dashicons dashicons-saved" style="vertical-align: middle;"></span>
                        設定を保存
                    </button>
                </div>

                <div id="save-message" style="margin-top: 20px;"></div>
            </div>

            <div class="card" style="max-width: 100%; margin-top: 20px;">
                <h2>動作テスト</h2>
                <p>実際のリンクがどのように変換されるかテストできます。</p>
                
                <div style="margin-bottom: 15px;">
                    <label for="test-url" style="display: block; margin-bottom: 5px; font-weight: 600;">テスト用URL</label>
                    <input type="text" id="test-url" class="regular-text" placeholder="https://yourdoll.jp/product/qtd207-lovedoll/" style="width: 100%; max-width: 600px;">
                </div>
                
                <button type="button" class="button" id="test-convert">変換テスト</button>
                
                <div id="test-result" style="margin-top: 15px; padding: 15px; background: #f0f0f1; border-radius: 4px; display: none;">
                    <strong>変換結果:</strong>
                    <div id="test-result-text" style="margin-top: 10px; font-family: monospace; word-break: break-all;"></div>
                </div>
            </div>

            <div class="card" style="max-width: 100%; margin-top: 20px;">
                <h2>📊 統計情報</h2>
                <div id="affiliate-stats">
                    <p>登録されているサイト数: <strong id="stats-total">0</strong></p>
                    <p>有効なサイト数: <strong id="stats-active">0</strong></p>
                </div>
            </div>
        </div>
    </div>

    <style>
        .affiliate-link-row {
            background: #fff;
        }
        .affiliate-link-row td {
            padding: 12px 10px;
            vertical-align: middle;
        }
        .affiliate-link-row input[type="text"] {
            width: 100%;
            padding: 6px 10px;
        }
        .affiliate-link-row input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        .preview-link {
            font-size: 11px;
            color: #666;
            word-break: break-all;
            font-family: monospace;
        }
        .delete-btn {
            color: #b32d2e;
            cursor: pointer;
            font-size: 20px;
        }
        .delete-btn:hover {
            color: #dc3232;
        }
        #save-message.success {
            color: #00a32a;
            font-weight: 600;
        }
        #save-message.error {
            color: #d63638;
            font-weight: 600;
        }
    </style>

    <script>
    (function($) {
        'use strict';

        // 初期データ
        let affiliateLinks = <?php echo json_encode($affiliate_links); ?>;
        
        // ページ読み込み時に既存データを表示
        $(document).ready(function() {
            renderAffiliateLinks();
            updateStats();
        });

        // アフィリエイトリンクを描画
        function renderAffiliateLinks() {
            const tbody = $('#affiliate-links-tbody');
            tbody.empty();

            if (affiliateLinks.length === 0) {
                tbody.append('<tr><td colspan="6" style="text-align: center; padding: 30px; color: #999;">まだサイトが登録されていません。「新しいサイトを追加」ボタンをクリックして追加してください。</td></tr>');
                return;
            }

            affiliateLinks.forEach((link, index) => {
                const row = createAffiliateRow(link, index);
                tbody.append(row);
            });

            // プレビューを更新
            updateAllPreviews();
        }

        // アフィリエイトリンクの行を作成
        function createAffiliateRow(link, index) {
            const previewUrl = link.domain ? `https://${link.domain}/example/product/` : '';
            const previewText = previewUrl && link.param ? `${previewUrl}${link.param}` : '設定してください';

            return `
                <tr class="affiliate-link-row" data-index="${index}">
                    <td style="text-align: center;">
                        <input type="checkbox" class="enabled-checkbox" ${link.enabled ? 'checked' : ''}>
                    </td>
                    <td>
                        <input type="text" class="site-name" value="${link.name || ''}" placeholder="例: YourDoll">
                    </td>
                    <td>
                        <input type="text" class="domain" value="${link.domain || ''}" placeholder="例: yourdoll.jp">
                    </td>
                    <td>
                        <input type="text" class="param" value="${link.param || ''}" placeholder="例: ?ref=kuuhaku-lovedoll">
                    </td>
                    <td>
                        <div class="preview-link">${previewText}</div>
                    </td>
                    <td style="text-align: center;">
                        <span class="dashicons dashicons-trash delete-btn" title="削除"></span>
                    </td>
                </tr>
            `;
        }

        // 新しいサイトを追加
        $('#add-affiliate-link').on('click', function() {
            affiliateLinks.push({
                name: '',
                domain: '',
                param: '',
                enabled: true
            });
            renderAffiliateLinks();
            updateStats();
        });

        // 削除ボタン
        $(document).on('click', '.delete-btn', function() {
            if (!confirm('このサイトを削除してもよろしいですか？')) {
                return;
            }
            const index = $(this).closest('tr').data('index');
            affiliateLinks.splice(index, 1);
            renderAffiliateLinks();
            updateStats();
        });

        // 入力時にプレビューを更新
        $(document).on('input', '.domain, .param', function() {
            updateAllPreviews();
        });

        // すべてのプレビューを更新
        function updateAllPreviews() {
            $('.affiliate-link-row').each(function() {
                const domain = $(this).find('.domain').val().trim();
                const param = $(this).find('.param').val().trim();
                const preview = $(this).find('.preview-link');

                if (domain && param) {
                    preview.text(`https://${domain}/example/product/${param}`);
                } else {
                    preview.text('設定してください');
                }
            });
        }

        // 設定を保存
        $('#save-affiliate-links').on('click', function() {
            // データを収集
            affiliateLinks = [];
            $('.affiliate-link-row').each(function() {
                const name = $(this).find('.site-name').val().trim();
                const domain = $(this).find('.domain').val().trim();
                const param = $(this).find('.param').val().trim();
                const enabled = $(this).find('.enabled-checkbox').is(':checked');

                if (domain && param) {
                    affiliateLinks.push({
                        name: name,
                        domain: domain,
                        param: param,
                        enabled: enabled
                    });
                }
            });

            // Ajax で保存
            $.ajax({
                url: ajaxurl,
                type: 'POST',
                data: {
                    action: 'save_affiliate_links',
                    nonce: '<?php echo wp_create_nonce('save_affiliate_links'); ?>',
                    links: JSON.stringify(affiliateLinks)
                },
                success: function(response) {
                    if (response.success) {
                        $('#save-message').text('✓ 設定を保存しました').addClass('success').removeClass('error');
                        setTimeout(() => $('#save-message').text(''), 3000);
                        updateStats();
                    } else {
                        $('#save-message').text('✗ 保存に失敗しました').addClass('error').removeClass('success');
                    }
                },
                error: function() {
                    $('#save-message').text('✗ 保存に失敗しました').addClass('error').removeClass('success');
                }
            });
        });

        // 変換テスト
        $('#test-convert').on('click', function() {
            const testUrl = $('#test-url').val().trim();
            if (!testUrl) {
                alert('テスト用URLを入力してください');
                return;
            }

            let convertedUrl = testUrl;
            let matched = false;

            affiliateLinks.forEach(link => {
                if (link.enabled && testUrl.includes(link.domain)) {
                    // URLにすでにクエリパラメータがあるかチェック
                    if (testUrl.includes('?')) {
                        // & で追加
                        const paramWithoutQuestion = link.param.replace(/^\?/, '');
                        convertedUrl = testUrl + '&' + paramWithoutQuestion;
                    } else {
                        // ? で追加
                        convertedUrl = testUrl + link.param;
                    }
                    matched = true;
                }
            });

            $('#test-result').show();
            if (matched) {
                $('#test-result-text').html(`
                    <div style="color: #00a32a; margin-bottom: 10px;">✓ マッチしました</div>
                    <div style="color: #666;">元のURL: <span style="color: #000;">${testUrl}</span></div>
                    <div style="color: #666; margin-top: 5px;">変換後: <span style="color: #2271b1; font-weight: 600;">${convertedUrl}</span></div>
                `);
            } else {
                $('#test-result-text').html(`
                    <div style="color: #d63638;">✗ マッチするサイトが見つかりませんでした</div>
                    <div style="color: #666; margin-top: 5px;">URL: ${testUrl}</div>
                `);
            }
        });

        // 統計情報を更新
        function updateStats() {
            const total = affiliateLinks.length;
            const active = affiliateLinks.filter(link => link.enabled).length;
            $('#stats-total').text(total);
            $('#stats-active').text(active);
        }

    })(jQuery);
    </script>
    <?php
}

// Ajax で設定を保存
add_action('wp_ajax_save_affiliate_links', 'lovedoll_save_affiliate_links');

function lovedoll_save_affiliate_links() {
    // Nonce チェック
    if (!isset($_POST['nonce']) || !wp_verify_nonce($_POST['nonce'], 'save_affiliate_links')) {
        wp_send_json_error('Invalid nonce');
        return;
    }

    // 権限チェック
    if (!current_user_can('manage_options')) {
        wp_send_json_error('Insufficient permissions');
        return;
    }

    // データを取得
    $links = isset($_POST['links']) ? json_decode(stripslashes($_POST['links']), true) : array();

    // データを保存
    update_option('lovedoll_affiliate_links', $links);

    wp_send_json_success();
}
