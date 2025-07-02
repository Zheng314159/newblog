import request from './request';

export const getStatistics = async () => {
  const response = await request.get("/config/statistics");
  return response;
};

export const getHealth = async () => {
  const response = await request.get("/config/health");
  return response;
}; 