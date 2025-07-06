import React from "react";
import "./Banner.css";

const Banner: React.FC = () => (
  <div className="banner">
    {/* 背景视频（优先） */}
    <video className="banner-bg-video" src="/banner.mp4" autoPlay loop muted playsInline poster="/banner.png" />
    {/* 背景图片（兜底） */}
    <div className="banner-bg-image" />
    {/* 半透明遮罩 */}
    <div className="banner-mask" />
    <div className="banner-content">
      <div className="banner-logo">
        <img src="/logo192.png" alt="Logo" />
      </div>
      <div className="banner-slogan">fastapi博客系统</div>
      <div className="banner-ad">[广告位招租]</div>
    </div>
  </div>
);

export default Banner; 