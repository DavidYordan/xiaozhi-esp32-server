-- 新增 NoVision 视觉禁用供应器与模型
DELETE FROM `ai_model_provider` WHERE `id` = 'SYSTEM_VLLM_novision';
INSERT INTO `ai_model_provider` (
  `id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`
) VALUES (
  'SYSTEM_VLLM_novision', 'VLLM', 'novision', 'No Vision（禁用视觉）', '[]', 0, 1, NOW(), 1, NOW()
);

DELETE FROM `ai_model_config` WHERE `id` = 'VLLM_NoVision';
INSERT INTO `ai_model_config` (
  `id`, `model_type`, `model_code`, `model_name`, `is_default`, `is_enabled`, `config_json`, `doc_link`, `remark`, `sort`, `creator`, `create_date`, `updater`, `update_date`
) VALUES (
  'VLLM_NoVision', 'VLLM', 'NoVision', '禁用视觉', 0, 1, '{"type":"novision"}', NULL, '禁用视觉能力，不暴露视觉接口', 0, 1, NOW(), 1, NOW()
);

-- 可选：将智能体模板的默认视觉模型改为 NoVision（按需启用）
-- UPDATE `ai_agent_template` SET `vllm_model_id` = 'VLLM_NoVision' WHERE `is_default` = 1;
