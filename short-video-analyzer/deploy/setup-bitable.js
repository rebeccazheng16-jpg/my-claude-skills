/**
 * 设置 Lark Bitable 表格字段
 * 创建 Short Video Analyzer 需要的所有字段
 */

const LARK_API_BASE = 'https://open.larksuite.com/open-apis';
const APP_ID = 'cli_a9fef0a93f385ed0';
const APP_SECRET = 'GxvwavRv5K02eDwVMws2VbHZSjbHt0cf';
const BITABLE_APP_TOKEN = 'XD1FbuEXnaK64TsuUC0lgKIZgLd';
const BITABLE_TABLE_ID = 'tblL8hnDFW3mZGmH';

// 需要创建的字段定义
const FIELDS_TO_CREATE = [
  {
    field_name: '视频链接',
    type: 15, // URL 类型
  },
  {
    field_name: '平台',
    type: 3, // Single Select
    property: {
      options: [
        { name: 'TikTok' },
        { name: '其他' }
      ]
    }
  },
  {
    field_name: '分析时间',
    type: 5, // DateTime
    property: {
      date_formatter: 'yyyy/MM/dd HH:mm'
    }
  },
  {
    field_name: '视频时长',
    type: 1, // Text
  },
  {
    field_name: '类型',
    type: 1, // Text
  },
  {
    field_name: '产品',
    type: 1, // Text
  },
  {
    field_name: '综合评分',
    type: 2, // Number
    property: {
      formatter: '0'
    }
  },
  {
    field_name: '核心卖点',
    type: 1, // Text
  },
  {
    field_name: '爆款原因',
    type: 1, // Text
  }
];

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

async function getExistingFields(token) {
  const response = await fetch(
    `${LARK_API_BASE}/bitable/v1/apps/${BITABLE_APP_TOKEN}/tables/${BITABLE_TABLE_ID}/fields`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`获取字段失败: ${data.msg}`);
  }
  return data.data.items || [];
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

  const data = await response.json();
  return data;
}

async function main() {
  console.log('='.repeat(50));
  console.log('  Lark Bitable 字段设置');
  console.log('='.repeat(50));
  console.log('');

  try {
    // 1. 获取 token
    console.log('1. 获取 tenant_access_token...');
    const token = await getTenantAccessToken();
    console.log('   ✓ Token 获取成功');

    // 2. 获取现有字段
    console.log('\n2. 检查现有字段...');
    const existingFields = await getExistingFields(token);
    const existingNames = existingFields.map(f => f.field_name);
    console.log(`   现有字段: ${existingNames.join(', ')}`);

    // 3. 创建缺失的字段
    console.log('\n3. 创建字段...');

    for (const field of FIELDS_TO_CREATE) {
      if (existingNames.includes(field.field_name)) {
        console.log(`   ⊖ "${field.field_name}" 已存在，跳过`);
        continue;
      }

      const result = await createField(token, field);
      if (result.code === 0) {
        console.log(`   ✓ "${field.field_name}" 创建成功`);
      } else {
        console.log(`   ✗ "${field.field_name}" 创建失败: ${result.msg}`);
      }

      // 避免请求过快
      await new Promise(r => setTimeout(r, 200));
    }

    // 4. 验证结果
    console.log('\n4. 验证字段...');
    const finalFields = await getExistingFields(token);
    console.log(`   最终字段列表 (${finalFields.length} 个):`);
    finalFields.forEach(f => {
      console.log(`   - ${f.field_name} (${f.ui_type || f.type})`);
    });

    console.log('\n' + '='.repeat(50));
    console.log('  设置完成!');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('\n错误:', error.message);
    process.exit(1);
  }
}

main();
