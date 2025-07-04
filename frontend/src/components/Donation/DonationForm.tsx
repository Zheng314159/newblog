import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Radio,
  Checkbox,
  InputNumber,
  message,
  Card,
  Space,
  Divider,
  Typography,
  Row,
  Col,
  App,
} from 'antd';
import { HeartOutlined, UserOutlined, MessageOutlined } from '@ant-design/icons';
import { createDonation, getDonationConfig, DonationConfig } from '../../api/donation';
import { useSelector } from 'react-redux';
import { RootState } from '../../app/store';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface DonationFormProps {
  onSuccess?: (donation: any) => void;
  onCancel?: () => void;
}

const DonationForm: React.FC<DonationFormProps> = ({ onSuccess, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<DonationConfig | null>(null);
  const [customAmount, setCustomAmount] = useState<number | null>(null);
  
  const user = useSelector((state: RootState) => state.user.userInfo);
  const { message } = App.useApp();

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await getDonationConfig();
      setConfig(response.data);
      
      // 如果有用户信息，自动填充姓名
      if (user) {
        form.setFieldsValue({
          donor_name: user.full_name || user.username,
          donor_email: user.email,
        });
      }
    } catch (error) {
      message.error('加载捐赠配置失败');
    }
  };

  const handleSubmit = async (values: any) => {
    if (!config?.is_enabled) {
      message.error('捐赠功能未启用');
      return;
    }

    setLoading(true);
    try {
      const response = await createDonation({
        ...values,
        amount: values.amount || customAmount || 0,
        currency: 'CNY',
      });

      message.success('捐赠记录创建成功！');
      onSuccess?.(response.data);
      
      // 重置表单
      form.resetFields();
      setCustomAmount(null);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建捐赠记录失败');
    } finally {
      setLoading(false);
    }
  };

  const presetAmounts = config?.preset_amounts 
    ? JSON.parse(config.preset_amounts) 
    : [5, 10, 20, 50, 100];

  const getPaymentMethodLabel = (method: string) => {
    const labels = {
      ALIPAY: '支付宝',
      WECHAT: '微信支付',
      PAYPAL: 'PayPal',
      BANK_TRANSFER: '银行转账',
      CRYPTO: '加密货币',
    };
    return labels[method as keyof typeof labels] || method;
  };

  const getDonationTypeLabel = (type: string) => {
    const labels = {
      ONE_TIME: '一次性捐赠',
      MONTHLY: '月度捐赠',
      YEARLY: '年度捐赠',
    };
    return labels[type as keyof typeof labels] || type;
  };

  if (!config) {
    return <div>加载中...</div>;
  }

  if (!config.is_enabled) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <HeartOutlined style={{ fontSize: '48px', color: '#ff4d4f' }} />
          <Title level={3}>捐赠功能暂未开放</Title>
          <Text type="secondary">感谢您的关注，捐赠功能正在准备中...</Text>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <HeartOutlined style={{ fontSize: '48px', color: '#ff4d4f' }} />
        <Title level={2}>{config.title}</Title>
        <Text type="secondary">{config.description}</Text>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          donation_type: 'ONE_TIME',
          is_anonymous: false,
        }}
      >
        {/* 捐赠者信息 */}
        <Form.Item
          label="捐赠者姓名"
          name="donor_name"
          rules={[{ required: true, message: '请输入捐赠者姓名' }]}
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="请输入您的姓名"
            maxLength={50}
          />
        </Form.Item>

        <Form.Item
          label="邮箱地址"
          name="donor_email"
          rules={[
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]}
        >
          <Input placeholder="可选，用于接收感谢邮件" />
        </Form.Item>

        <Form.Item
          label="留言"
          name="donor_message"
        >
          <TextArea
            prefix={<MessageOutlined />}
            placeholder="可选，留下您想说的话..."
            rows={3}
            maxLength={200}
            showCount
          />
        </Form.Item>

        <Form.Item name="is_anonymous" valuePropName="checked">
          <Checkbox>匿名捐赠</Checkbox>
        </Form.Item>

        <Divider />

        {/* 捐赠金额 */}
        <Form.Item label="捐赠金额">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Row gutter={[8, 8]}>
              {presetAmounts.map((amount: number) => (
                <Col key={amount}>
                  <Button
                    type={customAmount === amount ? 'primary' : 'default'}
                    onClick={() => {
                      setCustomAmount(amount);
                      form.setFieldsValue({ amount: amount });
                    }}
                  >
                    ¥{amount}
                  </Button>
                </Col>
              ))}
            </Row>
            
            <Form.Item name="amount" noStyle>
              <InputNumber
                placeholder="或输入自定义金额"
                min={0.01}
                max={99999}
                precision={2}
                style={{ width: '100%' }}
                onChange={(value) => setCustomAmount(value)}
                addonBefore="¥"
              />
            </Form.Item>
          </Space>
        </Form.Item>

        <Divider />

        {/* 捐赠类型 */}
        <Form.Item
          label="捐赠类型"
          name="donation_type"
          rules={[{ required: true, message: '请选择捐赠类型' }]}
        >
          <Radio.Group>
            <Space direction="vertical">
              <Radio value="ONE_TIME">{getDonationTypeLabel('ONE_TIME')}</Radio>
              <Radio value="MONTHLY">{getDonationTypeLabel('MONTHLY')}</Radio>
              <Radio value="YEARLY">{getDonationTypeLabel('YEARLY')}</Radio>
            </Space>
          </Radio.Group>
        </Form.Item>

        <Divider />

        {/* 支付方式 */}
        <Form.Item
          label="支付方式"
          name="payment_method"
          rules={[{ required: true, message: '请选择支付方式' }]}
        >
          <Radio.Group>
            <Space direction="vertical">
              {config.alipay_enabled && (
                <Radio value="ALIPAY">{getPaymentMethodLabel('ALIPAY')}</Radio>
              )}
              {config.wechat_enabled && (
                <Radio value="WECHAT">{getPaymentMethodLabel('WECHAT')}</Radio>
              )}
              {config.paypal_enabled && (
                <Radio value="PAYPAL">{getPaymentMethodLabel('PAYPAL')}</Radio>
              )}
              {config.bank_transfer_enabled && (
                <Radio value="BANK_TRANSFER">{getPaymentMethodLabel('BANK_TRANSFER')}</Radio>
              )}
              {config.crypto_enabled && (
                <Radio value="CRYPTO">{getPaymentMethodLabel('CRYPTO')}</Radio>
              )}
            </Space>
          </Radio.Group>
        </Form.Item>

        <Divider />

        {/* 提交按钮 */}
        <Form.Item>
          <Space style={{ width: '100%', justifyContent: 'center' }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              size="large"
              icon={<HeartOutlined />}
            >
              确认捐赠
            </Button>
            {onCancel && (
              <Button size="large" onClick={onCancel}>
                取消
              </Button>
            )}
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default DonationForm; 