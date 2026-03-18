/**
 * 添加完整分析字段到 Bitable
 */

const LARK_API_BASE = 'https://open.larksuite.com/open-apis';
const APP_ID = 'cli_a9fef0a93f385ed0';
const APP_SECRET = 'GxvwavRv5K02eDwVMws2VbHZSjbHt0cf';
const BITABLE_APP_TOKEN = 'XD1FbuEXnaK64TsuUC0lgKIZgLd';
const BITABLE_TABLE_ID = 'tblL8hnDFW3mZGmH';

// 需要添加的新字段
const NEW_FIELDS = [
  { field_name: '口播稿原文', type: 1 }, // Text
  { field_name: '口播稿中文', type: 1 }, // Text
  { field_name: '分镜脚本', type: 1 },   // Text
  { field_name: '关键学习点', type: 1 }, // Text
  { field_name: '脚本模板', type: 1 },   // Text
  { field_name: 'AI视频提示词', type: 1 }, // Text
];

async function getTenantAccessToken() {
  const response = await fetch(`${LARK_API_BASE}/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET })
  });
  const data = await response.json();
  if (data.code !== 0) throw new Error(`获取 token 失败: ${data.msg}`);
  return data.tenant_access_token;
}

async function getExistingFields(token) {
  const response = await fetch(
    `${LARK_API_BASE}/bitable/v1/apps/${BITABLE_APP_TOKEN}/tables/${BITABLE_TABLE_ID}/fields`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const data = await response.json();
  return (data.data?.items || []).map(f => f.field_name);
}

async function createField(token, fieldConfig) {
  const response = await fetch(
    `${LARK_API_BASE}/bitable/v1/apps/${BITABLE_APP_TOKEN}/tables/${BITABLE_TABLE_ID}/fields`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(fieldConfig)
    }
  );
  return response.json();
}

async function main() {
  console.log('添加完整分析字段到 Bitable...\n');

  const token = await getTenantAccessToken();
  const existingFields = await getExistingFields(token);
  console.log('现有字段:', existingFields.join(', '), '\n');

  for (const field of NEW_FIELDS) {
    if (existingFields.includes(field.field_name)) {
      console.log(`⊖ "${field.field_name}" 已存在`);
      continue;
    }

    const result = await createField(token, field);
    if (result.code === 0) {
      console.log(`✓ "${field.field_name}" 创建成功`);
    } else {
      console.log(`✗ "${field.field_name}" 失败: ${result.msg}`);
    }
    await new Promise(r => setTimeout(r, 200));
  }

  console.log('\n完成！');
}

main().catch(console.error);
