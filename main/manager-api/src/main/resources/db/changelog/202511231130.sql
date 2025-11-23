DELETE FROM `ai_model_provider` WHERE `id` = 'SYSTEM_Memory_memu';
INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
('SYSTEM_Memory_memu', 'Memory', 'memu', 'MemU记忆',
 '[{"key":"base_url","label":"服务地址","type":"string"},{"key":"modality","label":"模态","type":"string"},{"key":"serve_port","label":"资源服务端口","type":"number"}]',
 4, 1, NOW(), 1, NOW());
DELETE FROM `ai_model_config` WHERE `id` = 'Memory_memu';
INSERT INTO `ai_model_config` VALUES (
  'Memory_memu',
  'Memory',
  'memu',
  'MemU记忆',
  0,
  1,
  '{"type":"memu","base_url":"http://127.0.0.1:8765","modality":"conversation","serve_port":8003}',
  'https://memu.pro/docs#memory-apis',
  'MemU记忆配置说明：\n1. base_url 指向 memu-server 的服务地址（默认 http://127.0.0.1:8765）。\n2. serve_port 填写 xiaozhi-server 的 HTTP 服务端口，用于对外暴露 /memu/resources/{rid}（推荐与实际服务端口一致）。\n3. modality 建议使用 conversation。\n4. 保证 memu-server 可以访问到 resource_url（注意本机/局域网IP与防火墙放行）。',
  4,
  1,
  NOW(),
  1,
  NOW()
);
