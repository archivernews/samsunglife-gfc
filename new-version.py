#!/usr/bin/env python3
"""Copy a self-contained landing page; keep earlier versions intact."""
import argparse
from pathlib import Path
from datetime import date
import json
import re

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description='새 GFC 페이지 초안을 만들고 최신 페이지로 지정합니다.')
parser.add_argument('--date', required=True, help='YYYY-MM-DD')
parser.add_argument('--version', required=True, help='v2, v3 등')
parser.add_argument('--title', required=True)
args = parser.parse_args()
date.fromisoformat(args.date)
if not re.fullmatch(r'v[1-9][0-9]*', args.version):
    parser.error('버전은 v1, v2 형식이어야 합니다.')
manifest_path = root / 'versions.json'
manifest = json.loads(manifest_path.read_text())
previous = next(v for v in manifest['versions'] if v['id'] == manifest['latest'])
slug = f'gfc-{args.date}-{args.version}'
target = root / f'{slug}.html'
if target.exists() or any(v['id'] == slug for v in manifest['versions']):
    parser.error('이미 존재하는 버전입니다. 기존 페이지를 덮어쓰지 않습니다.')
html = (root / previous['path']).read_text()
html = html.replace(previous['id'], slug).replace(previous['date'], args.date)
html = html.replace(f'version:"{previous["version"]}"', f'version:"{args.version}"')
html = html.replace(f'· {previous["version"]}<', f'· {args.version}<')
target.write_text(html)
manifest['versions'].insert(0, dict(id=slug,date=args.date,version=args.version,title=args.title,status='draft',path=target.name))
manifest['latest'] = slug
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(root / 'index.html').write_text(html)
print(f'생성: {target.name}\n이전 버전은 보존했습니다. 새 페이지의 문구·설정·고지를 수정하고 index.html에도 동일하게 반영하세요.')
