# R2FileLister

**R2FileLister** 是一个基于 Python 开发的工具，用于自动扫描 Cloudflare R2 存储桶中的文件和文件夹，生成目录结构的静态 HTML 页面，并自动上传到存储空间。生成的网页界面美观简洁，支持中文文件名、多层目录、文件大小显示等功能，方便用户通过浏览器查看和下载文件。


## 功能特点

- **自动生成目录列表**  
  扫描 Cloudflare R2 存储桶中的所有文件和文件夹，自动为每个目录生成 `index.html` 页面，实现类似文件管理器的浏览体验。

- **多层子目录支持**  
  自动处理多级目录结构，每个子目录均生成独立的 `index.html` 页面，并提供返回上一层的按钮，方便层级导航。

- **显示文件大小**  
  在生成的文件列表中，会显示每个文件的大小，并对文件夹内所有文件的总大小进行统计，以人性化的格式展示（例如 KB、MB、GB 等）。

- **中文文件名支持**  
  完全支持中文文件名和目录名，确保在生成的网页中中文字符正常显示。

- **图标标识**  
  利用 Font Awesome 图标区分文件和文件夹，提升用户体验，直观显示文件类型。

- **自动上传 HTML 文件**  
  生成的 HTML 页面会自动上传回 Cloudflare R2 存储桶，保证在线访问最新的目录列表。

- **简洁美观的 UI**  
  整体界面设计简洁清爽，类似于 Caddy 文件管理器，提供舒适的文件浏览体验。

- **轻松使用**  
  只需简单配置访问密钥与存储桶信息，然后运行 `python main.py` 即可快速生成并上传目录页面。

## 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/bravexist/R2FileLister.git
   cd R2FileLister
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **配置 Cloudflare R2**

   - 创建一个新的 Cloudflare R2 存储桶。
   - 获取存储桶的访问密钥和密钥 ID。
   - 绑定自定义域名。（可选）
   - 将访问密钥和密钥 ID 配置到 `config.json` 文件中。

4. **运行程序**

   ```bash
   python main.py
   ```

5. **访问目录列表**

   在浏览器中访问 `https://自定义域名/index.html`，即可看到生成的目录列表。此处可以在cloudflare设置重定向到index.html


## 注意事项

- 请确保 Cloudflare R2 存储桶的访问权限正确，否则可能会导致上传失败。
- 请确保 `config.json` 文件中的访问密钥和密钥 ID 正确，否则可能会导致上传失败。

## 示例

您可以访问 [clash.bravexist.cn](https://clash.bravexist.cn) 查看在线演示。

![示例截图](https://img.bravexist.cn/2025/02/05/06f5ebabeeacc69fd08f6dc5e4b1b192.png)

## 感谢

- 感谢 [Font Awesome](https://fontawesome.com/) 提供的图标支持。
- 感谢 [Caddy](https://caddyserver.com/) 提供的文件管理器灵感。
- 感谢 [Cloudflare R2](https://www.cloudflare.com/r2/) 提供的云存储服务。
- 感谢 [ChatGPT](https://chatgpt.com/) 提供的智能助手。

## 许可证

本项目采用 MIT 许可证。这意味着您可以自由地使用、修改和分发本项目，但需要保留原始许可证和版权声明。

详细信息请参阅 [LICENSE](LICENSE) 文件。
