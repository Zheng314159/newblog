import React, { useEffect, useState } from "react";
import { useParams, useNavigate, unstable_usePrompt as usePrompt } from "react-router-dom";
import { Card, Form, Input, Button, Select, Spin, Row, Col, Divider, Space, App } from "antd";
import { createArticle, getArticle, updateArticle } from "../../api/article";
import MarkdownEditor from "../../components/MarkdownEditor/MarkdownEditor";
import MarkdownViewer from "../../components/MarkdownViewer/MarkdownViewer";
import { getTags } from "../../api/tag";
import { useSelector } from "react-redux";
import { RootState } from "../../app/store";
import MediaUpload from "../../components/Upload/MediaUpload";

const { Option } = Select;
const { TextArea } = Input;

const ArticleEdit: React.FC = () => {
  const { id } = useParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [tags, setTags] = useState<string[]>([]);
  const [content, setContent] = useState("");
  const [previewMode, setPreviewMode] = useState<'split' | 'edit' | 'preview'>('split');
  const [articleAuthorId, setArticleAuthorId] = useState<number | null>(null);
  const { userInfo } = useSelector((state: RootState) => state.user);
  const navigate = useNavigate();
  const { message } = App.useApp();
  const [saveStatus, setSaveStatus] = useState<'published' | 'draft'>('draft');
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    getTags().then((res: any) => {
      const tagArr = res.tags || res.data || [];
      // 过滤无效项，全部转字符串并去除空白，再去重
      const uniqueTags = Array.from(
        new Set(
          tagArr
            .filter((t: any) => {
              if (t === null || t === undefined) return false;
              const str = typeof t === 'string' ? t : (t.name || t.id || JSON.stringify(t));
              return !!str && String(str).trim() !== '';
            })
            .map((t: any) => {
              if (typeof t === 'string') return t.trim();
              if (typeof t === 'object' && t !== null) {
                return (t.name || t.id || JSON.stringify(t)).trim();
              }
              return String(t).trim();
            })
        )
      ) as string[];
      setTags(uniqueTags);
    });
    if (id && id !== 'new') {
      setLoading(true);
      getArticle(id).then((res: any) => {
        const data = res.data || res;
        // 过滤初始值中的空白标签
        const cleanTags = (data.tags || []).filter(
          (t: any) => {
            if (t === null || t === undefined) return false;
            const str = typeof t === 'string' ? t : (t.name || t.id || JSON.stringify(t));
            return !!str && String(str).trim() !== '';
          }
        ).map(
          (t: any) => typeof t === 'string' ? t.trim() : (t.name || t.id || JSON.stringify(t)).trim()
        );
        form.setFieldsValue({ ...data, tags: cleanTags });
        setContent(data.content || "");
        setArticleAuthorId(data.author?.id ?? null);
        setLoading(false);
      });
    }
  }, [id, form]);

  // 监听内容变更，标记未保存
  useEffect(() => {
    setIsDirty(true);
  }, [content]);

  // 页面关闭拦截
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [isDirty]);

  const handleSave = async (status: 'published' | 'draft', silent = false) => {
    setSaveStatus(status);
    form.submit();
    if (!silent) setIsDirty(false);
  };

  // 权限校验：仅作者可编辑
  if (id && articleAuthorId !== null && userInfo && userInfo.id !== articleAuthorId) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'red', fontSize: 18 }}>
        无权限编辑该文章
      </div>
    );
  }

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // 过滤掉空白标签
      const cleanTags = (values.tags || []).filter(
        (t: any) => !!t && String(t).trim() !== ''
      ).map((t: any) => String(t).trim());
      const data = {
        title: values.title?.trim() || "",
        content: content?.trim() || "",
        tags: cleanTags,
        summary: values.summary?.trim() || content?.slice(0, 100) || "",
        status: saveStatus,
        has_latex: /\$[^$]+\$|\$\$[\s\S]*?\$\$/.test(content),
        latex_content: null
      };
      if (!data.title || !data.content) {
        message.error("标题和内容不能为空");
        setLoading(false);
        return;
      }
      if (id && id !== 'new') {
        await updateArticle(id, { ...data });
        message.success(saveStatus === 'published' ? "文章发布成功" : "草稿已保存");
      } else {
        const res: any = await createArticle(data);
        message.success(saveStatus === 'published' ? "文章发布成功" : "草稿已保存");
        navigate(`/article/${res.id || res.data?.id}`);
      }
      setIsDirty(false);
    } catch (e: any) {
      message.error(e.message || "操作失败");
    } finally {
      setLoading(false);
    }
  };

  const handleInsertMedia = (url: string, type: string) => {
    let insertText = "";
    if (type === "image") {
      insertText = `![](${url})`;
    } else if (type === "video") {
      insertText = `![视频](${url})`;
    } else if (type === "pdf") {
      insertText = `[PDF文档](${url})`;
    }
    setContent((prev) => prev + (prev && !prev.endsWith("\n") ? "\n" : "") + insertText + "\n");
  };

  const renderEditor = () => (
    <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: '10px' }}>
        <Space>
          <Button 
            type={previewMode === 'edit' ? 'primary' : 'default'}
            onClick={() => setPreviewMode('edit')}
          >
            编辑模式
          </Button>
          <Button 
            type={previewMode === 'split' ? 'primary' : 'default'}
            onClick={() => setPreviewMode('split')}
          >
            分屏模式
          </Button>
          <Button 
            type={previewMode === 'preview' ? 'primary' : 'default'}
            onClick={() => setPreviewMode('preview')}
          >
            预览模式
          </Button>
        </Space>
      </div>
      
      {previewMode === 'edit' && (
        <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: '6px' }}>
          <MarkdownEditor 
            value={content} 
            onChange={setContent} 
            height={550}
            placeholder="请输入文章内容... (支持 Markdown 和 LaTeX 公式)"
          />
        </div>
      )}
      
      {previewMode === 'preview' && (
        <div style={{ 
          flex: 1, 
          border: '1px solid #d9d9d9', 
          borderRadius: '6px',
          padding: '16px',
          overflow: 'auto',
          backgroundColor: '#fff'
        }}>
          <MarkdownViewer content={content} />
        </div>
      )}
    </div>
  );

  const renderSplitView = () => (
    <Row gutter={16} style={{ height: '600px' }}>
      <Col span={12}>
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ marginBottom: '10px', fontSize: '14px', fontWeight: 'bold', color: '#666' }}>
            编辑区域
          </div>
          <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: '6px', marginBottom: 8 }}>
            <MarkdownEditor 
              value={content} 
              onChange={setContent} 
              height={550}
              placeholder="请输入文章内容... (支持 Markdown 和 LaTeX 公式)"
            />
          </div>
          <div style={{ marginBottom: 0 }}>
            <MediaUpload onUpload={handleInsertMedia} />
          </div>
        </div>
      </Col>
      <Col span={12}>
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ marginBottom: '10px', fontSize: '14px', fontWeight: 'bold', color: '#666' }}>
            实时预览
          </div>
          <div style={{ 
            flex: 1, 
            border: '1px solid #d9d9d9', 
            borderRadius: '6px',
            padding: '16px',
            overflow: 'auto',
            backgroundColor: '#fff'
          }}>
            <MarkdownViewer content={content} />
          </div>
        </div>
      </Col>
    </Row>
  );

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      <Card 
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{id && id !== 'new' ? "编辑文章" : "发布新文章"}</span>
            <Space>
              <Button onClick={() => navigate(-1)}>返回</Button>
              <Button type="primary" onClick={() => handleSave('published')} loading={loading}>
                发布文章
              </Button>
              <Button  type="primary" onClick={() => handleSave('draft')} loading={loading}>
                保存为草稿
              </Button>
            </Space>
          </div>
        }
        extra={
          <div style={{ fontSize: '12px', color: '#666' }}>
            字数统计: {content.length} 字符
          </div>
        }
      >
        <Spin spinning={loading}>
          <Form form={form} layout="vertical" onFinish={onFinish}>
            <Row gutter={16}>
              <Col span={16}>
                <Form.Item name="title" label="文章标题" rules={[{ required: true, message: '请输入文章标题' }]}>
                  <Input size="large" placeholder="请输入文章标题..." />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="tags" label="标签">
                  <Select 
                    mode="tags" 
                    size="large"
                    placeholder="选择或输入标签..."
                    style={{ width: "100%" }}
                    filterOption={(input, option) => !!option?.value && option.value.toString().toLowerCase().includes(input.toLowerCase())}
                  >
                    {tags.filter(tag => tag && tag.trim() !== '').map((tag) => (
                      <Option key={tag} value={tag}>
                        {tag}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Divider />

            <div style={{ marginBottom: '16px' }}>
              <div style={{ 
                padding: '12px', 
                backgroundColor: '#f6f8fa', 
                borderRadius: '6px',
                border: '1px solid #e1e4e8'
              }}>
                <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>
                  📝 编辑提示
                </div>
                <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.5' }}>
                  <div>• 支持 <strong>Markdown</strong> 语法：标题、列表、链接、图片等</div>
                  <div>• 支持 <strong>LaTeX</strong> 数学公式：行内公式 $...$ 和块级公式 $$...$$</div>
                  <div>• 支持 <strong>代码高亮</strong>：使用 ``` 包围代码块</div>
                  <div>• 使用分屏模式可以实时预览渲染效果</div>
                </div>
              </div>
            </div>

            <Form.Item label="文章内容" required>
              {previewMode === 'split' ? renderSplitView() : renderEditor()}
            </Form.Item>

            <Divider />

            <div style={{ position: 'sticky', bottom: 0, background: '#fff', zIndex: 10, padding: '16px 0 0 0', marginTop: 32, borderTop: '1px solid #f0f0f0', textAlign: 'center' }}>
              <Space size="large">
                <Button size="large" onClick={() => navigate(-1)}>
                  取 消
                </Button>
                <Button 
                  type="primary" 
                  size="large" 
                  htmlType="submit" 
                  loading={loading}
                  onClick={() => handleSave('published')}
                >
                  {id && id !== 'new' ? "保存修改" : "发布文章"}
                </Button>
              </Space>
            </div>
          </Form>
        </Spin>
      </Card>
    </div>
  );
};

export default ArticleEdit;