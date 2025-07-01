import React, { useEffect, useState } from "react";
import { List, Tag, Typography, Spin, Card, Image, message, App } from "antd";
import { getArticles } from "../../api/article";
import { getMediaList } from "../../api/upload";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;

const Home: React.FC = () => {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [media, setMedia] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    getArticles({ status: 'published' }).then((res) => {
      const allArticles = res.items || res.data || [];
      const adminArticles = allArticles.filter((item: any) => item.author?.role === 'ADMIN');
      setArticles(adminArticles);
      setLoading(false);
    });
    // 获取多媒体
    getMediaList()
      .then((res) => setMedia((res.data || []).filter((m: any) => m.uploader_role === 'ADMIN')))
      .catch(() => message.error("获取多媒体文件失败"));
  }, []);

  return (
    <App>
      <div>
        <Title level={2}>最新文章</Title>
        <Spin spinning={loading}>
          <List
            itemLayout="vertical"
            dataSource={articles}
            renderItem={item => (
              <List.Item
                key={item.id}
                onClick={() => navigate(`/article/${item.id}`)}
                style={{ cursor: "pointer" }}
                extra={item.tags && item.tags.map((tag: any) => <Tag key={typeof tag === 'string' ? tag : tag.name}>{typeof tag === 'string' ? tag : tag.name}</Tag>)}
              >
                <List.Item.Meta
                  title={item.title}
                  description={`作者: ${item.author?.username || "匿名"} | 发布时间: ${item.created_at?.slice(0, 10)}`}
                />
                <div>{item.summary || item.content?.slice(0, 120) + "..."}</div>
              </List.Item>
            )}
          />
        </Spin>
        <div style={{ marginBottom: 32 }}>
          <Title level={3}>最新多媒体</Title>
          <div style={{ display: "flex", gap: 16 }}>
            {media.filter(m => m.type === "image").slice(0,3).map(img => (
              <Card key={img.filename} hoverable style={{ width: 120 }} cover={<Image src={img.url} alt={img.filename} style={{ height: 80, objectFit: "cover" }} />} actions={[<a href={img.url} download target="_blank" rel="noopener noreferrer">下载</a>]} />
            ))}
            {media.filter(m => m.type === "video").slice(0,3).map(vid => (
              <Card key={vid.filename} hoverable style={{ width: 160 }} cover={<video src={vid.url} controls style={{ width: "100%", height: 80, objectFit: "cover" }} />} actions={[<a href={vid.url} download target="_blank" rel="noopener noreferrer">下载</a>]} />
            ))}
          </div>
        </div>
      </div>
    </App>
  );
};

export default Home; 