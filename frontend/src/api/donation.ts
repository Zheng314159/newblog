import request from './request';

// 捐赠配置接口
export interface DonationConfig {
  id: number;
  is_enabled: boolean;
  title: string;
  description: string;
  alipay_enabled: boolean;
  wechat_enabled: boolean;
  paypal_enabled: boolean;
  bank_transfer_enabled: boolean;
  crypto_enabled: boolean;
  preset_amounts: string;
  total_donations: number;
  total_amount: number;
}

// 捐赠记录接口
export interface DonationRecord {
  id: number;
  donor_name: string;
  donor_email?: string;
  donor_message?: string;
  is_anonymous: boolean;
  amount: number;
  currency: string;
  donation_type: 'ONE_TIME' | 'MONTHLY' | 'YEARLY';
  payment_method: 'ALIPAY' | 'WECHAT' | 'PAYPAL' | 'BANK_TRANSFER' | 'CRYPTO';
  payment_status: 'PENDING' | 'SUCCESS' | 'FAILED' | 'CANCELLED';
  transaction_id?: string;
  user_id?: number;
  created_at: string;
  updated_at: string;
  paid_at?: string;
}

// 捐赠目标接口
export interface DonationGoal {
  id: number;
  title: string;
  description: string;
  target_amount: number;
  current_amount: number;
  currency: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  is_completed: boolean;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

// 捐赠统计接口
export interface DonationStats {
  total_donations: number;
  total_amount: number;
  currency: string;
  monthly_donations: number;
  monthly_amount: number;
  active_goals: number;
  completed_goals: number;
}

// 创建捐赠请求接口
export interface CreateDonationRequest {
  donor_name: string;
  donor_email?: string;
  donor_message?: string;
  is_anonymous: boolean;
  amount: number;
  currency: string;
  donation_type: 'ONE_TIME' | 'MONTHLY' | 'YEARLY';
  payment_method: 'ALIPAY' | 'WECHAT' | 'PAYPAL' | 'BANK_TRANSFER' | 'CRYPTO';
}

// 捐赠配置API
export const getDonationConfig = () => {
  return request.get<DonationConfig>('/donation/config');
};

export const updateDonationConfig = (config: Partial<DonationConfig>) => {
  return request.put<DonationConfig>('/donation/config', config);
};

// 捐赠记录API
export const createDonation = (data: CreateDonationRequest) => {
  return request.post<DonationRecord>('/donation/create', data);
};

export const getDonationRecords = (params?: {
  skip?: number;
  limit?: number;
  status_filter?: string;
}) => {
  return request.get<DonationRecord[]>('/donation/records', { params });
};

export const getMyDonationRecords = () => {
  return request.get<DonationRecord[]>('/donation/records/my');
};

export const updateDonationStatus = (
  donationId: number,
  status: string,
  transactionId?: string
) => {
  return request.put(`/donation/records/${donationId}/status`, {
    status,
    transaction_id: transactionId,
  });
};

// 捐赠目标API
export const getDonationGoals = (activeOnly: boolean = true) => {
  return request.get<DonationGoal[]>('/donation/goals', {
    params: { active_only: activeOnly },
  });
};

export const createDonationGoal = (data: {
  title: string;
  description: string;
  target_amount: number;
  currency: string;
  start_date: string;
  end_date?: string;
}) => {
  return request.post<DonationGoal>('/donation/goals', data);
};

export const updateDonationGoal = (
  goalId: number,
  data: Partial<DonationGoal>
) => {
  return request.put<DonationGoal>(`/donation/goals/${goalId}`, data);
};

export const deleteDonationGoal = (goalId: number) => {
  return request.delete(`/donation/goals/${goalId}`);
};

// 捐赠统计API
export const getDonationStats = () => {
  return request.get<DonationStats>('/donation/stats');
};

export const getPublicDonationStats = () => {
  return request.get<{
    total_donations: number;
    total_amount: number;
    currency: string;
    active_goals: number;
  }>('/donation/public-stats');
}; 