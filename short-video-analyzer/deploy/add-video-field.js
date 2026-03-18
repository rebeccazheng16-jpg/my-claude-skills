/**
 * 添加视频文件字段到 Bitable
 */

const LARK_API_BASE = 'https://open.larksuite.com/open-apis';
const APP_ID = 'cli_a9fef0a93f385ed0';
const APP_SECRET = 'GxvwavRv5K02eDwVMws2VbHZSjbHt0cf';
const BITABLE_APP_TOKEN = 'XD1FbuEXnaK64TsuUC0lgKIZgLd';
const BITABLE_TABLE_ID = 'tblL8hnDFW3mZGmH';

async function getTenantAccessToken() {
  const response = await fetch(`${LARK_API_BASE}/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      app_id: APP_ID,
      app_secret: APP_SECRET
    })
  });

  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`获取 token 失败: ${data.msg}`);
  }
  return data.tenant_access_token;
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
  console.log('添加"视频文件"字段到 Bitable...');

  const token = await getTenantAccessToken();
  console.log('Token 获取成功');

  const result = await createField(token, {
    field_name: '视频文件',
    type: 15, // URL 类型
  });

  if (result.code === 0) {
    console.log('✓ "视频文件" 字段创建成功');
  } else {
    console.log('创建结果:', result.msg);
  }
}

main().catch(console.error);
