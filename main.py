#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: qiao xiong
# datetime: 2025/2/5 21:04
# name: main

import os
import boto3
import json
from urllib.parse import quote

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def configure_r2(config):
    return boto3.client('s3',
                        endpoint_url=config['endpoint_url'],
                        aws_access_key_id=config['aws_access_key_id'],
                        aws_secret_access_key=config['aws_secret_access_key'],
                        region_name=config['region_name'])

def ensure_output_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def bytes_to_human(n):
    """将字节数转换为人类可读格式"""
    for unit in ['B','KB','MB','GB','TB','PB']:
        if n < 1024:
            return f"{n:.2f}{unit}"
        n /= 1024
    return f"{n:.2f}PB"

def compute_folder_size(bucket_client, bucket_name, prefix):
    """递归计算文件夹内所有文件的大小，排除掉生成的 index.html 文件"""
    total_size = 0
    continuation_token = None
    while True:
        params = {'Bucket': bucket_name, 'Prefix': prefix}
        if continuation_token:
            params['ContinuationToken'] = continuation_token
        response = bucket_client.list_objects_v2(**params)
        if 'Contents' in response:
            for obj in response['Contents']:
                if not obj['Key'].endswith("index.html"):
                    total_size += obj['Size']
        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break
    return total_size

def get_files_and_dirs(bucket_client, bucket_name, prefix=""):
    objects = bucket_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    files = []
    dirs = []
    if 'Contents' in objects:
        for obj in objects['Contents']:
            # 排除掉自动生成的 index.html
            if obj['Key'] != prefix + 'index.html':
                files.append({"Key": obj['Key'], "Size": obj['Size']})
    if 'CommonPrefixes' in objects:
        for obj in objects['CommonPrefixes']:
            dirs.append(obj['Prefix'])
    return files, dirs

def generate_html_for_directory(bucket_client, bucket_name, dir_name, files, dirs, base_url):
    # 去除末尾斜杠，便于处理
    dir_clean = dir_name.rstrip("/")
    # 当前目录显示名称仅取最后一级，如果为空则显示“根目录”
    display_name = dir_clean.split("/")[-1] if dir_clean else "根目录"
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .list-group-item {{
            border-radius: 0.375rem;
            position: relative;
        }}
        h1 {{
            color: #007bff;
        }}
        .nav-link {{
            color: #007bff;
        }}
        .nav-link:hover {{
            text-decoration: none;
            color: #0056b3;
        }}
        .nav-button {{
            margin-bottom: 20px;
            padding: 10px;
            font-size: 16px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
        }}
        .size-info {{
            position: absolute;
            right: 15px;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>{display_name}</h1>
    """
    # 当当前目录不为空时显示返回上一层按钮
    if dir_clean:
        parent = dir_clean.rsplit("/", 1)[0] if "/" in dir_clean else ""
        if parent:
            parent_link = f"{base_url}/{parent}/index.html"
        else:
            parent_link = f"{base_url}/index.html"
        html_content += f'<button class="nav-button" onclick="window.location.href=\'{parent_link}\'">返回上一层</button>'

    html_content += "<ul class='list-group'>"

    # 列出子目录，显示名称和文件夹大小
    for subdir in dirs:
        subdir_clean = subdir.rstrip("/")
        subdir_name = subdir_clean.split("/")[-1]
        folder_size = compute_folder_size(bucket_client, bucket_name, subdir)
        human_size = bytes_to_human(folder_size)
        html_content += f'<li class="list-group-item d-flex align-items-center"><i class="fas fa-folder me-2"></i><a class="nav-link" href="{quote(subdir_name)}/index.html">{subdir_name}</a><span class="size-info">{human_size}</span></li>'

    # 列出当前目录下的文件，显示文件大小
    for file in files:
        file_name = file["Key"].split("/")[-1]
        human_size = bytes_to_human(file["Size"])
        html_content += f'<li class="list-group-item d-flex align-items-center"><i class="fas fa-file me-2"></i><a class="nav-link" href="{base_url}/{file["Key"]}">{file_name}</a><span class="size-info">{human_size}</span></li>'

    html_content += "</ul></div></body></html>"

    # 输出目录，若 dir_name 为空则输出到 resulthtml 根目录
    output_dir = os.path.join('resulthtml', dir_name) if dir_clean else 'resulthtml'
    ensure_output_directory(output_dir)
    local_file_path = os.path.join(output_dir, 'index.html')
    with open(local_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return local_file_path

def upload_to_r2(s3_client, file_path, bucket_name, s3_key):
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"上传成功：{file_path} -> {s3_key}")
    except Exception as e:
        print(f"上传失败：{e}")

def get_all_files(bucket_client, bucket_name, base_url, prefix=""):
    files, dirs = get_files_and_dirs(bucket_client, bucket_name, prefix)
    local_file_path = generate_html_for_directory(bucket_client, bucket_name, prefix, files, dirs, base_url)
    upload_to_r2(bucket_client, local_file_path, bucket_name, f'{prefix}index.html')
    all_files = [file["Key"] for file in files]
    for sub_prefix in dirs:
        sub_files = get_all_files(bucket_client, bucket_name, base_url, sub_prefix)
        all_files.extend(sub_files)
    return all_files

if __name__ == '__main__':
    config = load_config()
    r2 = configure_r2(config)
    bucket_name = config['bucket_name']
    base_url = config['base_url']
    all_files = get_all_files(bucket_client=r2, bucket_name=bucket_name, prefix="", base_url=base_url)
    print(f"总文件数：{len(all_files)}")
