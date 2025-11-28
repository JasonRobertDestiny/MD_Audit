import argparse
from pathlib import Path
from typing import List
from md_audit.config import load_config
from md_audit.analyzer import MarkdownSEOAnalyzer
from md_audit.reporter import MarkdownReporter
from md_audit.models.data_models import SEOReport


def main():
    parser = argparse.ArgumentParser(
        description="Markdown SEO诊断工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m md_audit.main analyze article.md
  python -m md_audit.main analyze article.md -k "Python" "SEO"
  python -m md_audit.main analyze article.md --config custom.json -o report.md
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # analyze子命令
    analyze_parser = subparsers.add_parser('analyze', help='分析Markdown文件或目录')
    analyze_parser.add_argument('path', type=str, help='Markdown文件路径或目录路径')
    analyze_parser.add_argument('-k', '--keywords', nargs='+', help='目标关键词（可选）')
    analyze_parser.add_argument('--config', type=str, help='配置文件路径（可选）')
    analyze_parser.add_argument('-o', '--output', type=str, help='输出报告路径（文件或目录）')
    analyze_parser.add_argument('--no-ai', action='store_true', help='禁用AI分析')
    analyze_parser.add_argument('--workers', type=int, default=4, help='批量分析时的并发工作线程数（默认4）')

    # serve子命令（Web服务）
    serve_parser = subparsers.add_parser('serve', help='启动Web服务')
    serve_parser.add_argument('--host', type=str, default='127.0.0.1', help='服务器地址（默认127.0.0.1）')
    serve_parser.add_argument('--port', type=int, default=8000, help='服务器端口（默认8000）')
    serve_parser.add_argument('--reload', action='store_true', help='开发模式：代码变更自动重载')

    args = parser.parse_args()

    if args.command == 'analyze':
        # 加载配置
        config = load_config(args.config)

        # 覆盖AI开关
        if args.no_ai:
            config.enable_ai_analysis = False

        # 验证路径存在
        target_path = Path(args.path)
        if not target_path.exists():
            print(f"错误：路径不存在 {args.path}")
            return 1

        # 初始化分析器和报告器
        analyzer = MarkdownSEOAnalyzer(config)
        reporter = MarkdownReporter()

        # 判断是文件还是目录
        if target_path.is_file():
            # 单文件模式
            print(f"正在分析 {args.path} ...")
            report = analyzer.analyze(str(target_path), user_keywords=args.keywords)

            # 生成报告
            report_md = reporter.generate(report)

            # 输出
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_md)
                print(f"✅ 报告已保存到 {args.output}")
            else:
                print("\n" + report_md)

            # 返回状态码（基于得分）
            return 0 if report.total_score >= 70 else 1

        elif target_path.is_dir():
            # 批量目录模式
            print(f"批量分析目录: {args.path}")
            reports = analyzer.analyze_directory(
                str(target_path),
                user_keywords=args.keywords,
                max_workers=args.workers
            )

            if not reports:
                print("未生成任何报告")
                return 1

            # 输出批量报告
            if args.output:
                output_dir = Path(args.output)
                output_dir.mkdir(parents=True, exist_ok=True)

                # 为每个文件生成独立报告
                for report in reports:
                    rel_path = Path(report.file_path).relative_to(target_path)
                    report_filename = rel_path.with_suffix('.report.md').name
                    report_path = output_dir / report_filename

                    report_md = reporter.generate(report)
                    with open(report_path, 'w', encoding='utf-8') as f:
                        f.write(report_md)

                print(f"✅ 已保存 {len(reports)} 个报告到 {args.output}/")

                # 生成汇总报告
                summary_md = _generate_summary(reports, str(target_path))
                summary_path = output_dir / "SUMMARY.md"
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(summary_md)
                print(f"✅ 汇总报告已保存到 {summary_path}")

            else:
                # 终端输出汇总
                summary_md = _generate_summary(reports, str(target_path))
                print("\n" + summary_md)

            # 返回状态码（批量模式：平均分>=70为成功）
            avg_score = sum(r.total_score for r in reports) / len(reports)
            return 0 if avg_score >= 70 else 1

        else:
            print(f"错误：路径既不是文件也不是目录 {args.path}")
            return 1

    elif args.command == 'serve':
        # 启动Web服务
        try:
            import uvicorn
        except ImportError:
            print("错误：未安装Web服务依赖")
            print("请运行：pip install 'fastapi[all]' uvicorn slowapi")
            return 1

        print("=" * 50)
        print("MD Audit Web服务")
        print("=" * 50)
        print(f"服务地址: http://{args.host}:{args.port}")
        print(f"API文档: http://{args.host}:{args.port}/docs")
        print(f"健康检查: http://{args.host}:{args.port}/api/health")
        print("=" * 50)
        print("按Ctrl+C停止服务")
        print()

        # 启动uvicorn
        uvicorn.run(
            "web.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
        return 0

    else:
        parser.print_help()
        return 0


def _generate_summary(reports: List[SEOReport], base_dir: str) -> str:
    """
    生成批量分析汇总报告

    Args:
        reports: 所有报告列表
        base_dir: 基础目录路径

    Returns:
        Markdown格式的汇总报告
    """
    total = len(reports)
    avg_score = sum(r.total_score for r in reports) / total if total > 0 else 0

    # 分数分布统计
    excellent = sum(1 for r in reports if r.total_score >= 85)
    good = sum(1 for r in reports if 70 <= r.total_score < 85)
    medium = sum(1 for r in reports if 50 <= r.total_score < 70)
    poor = sum(1 for r in reports if r.total_score < 50)

    # 按分数排序（降序）
    sorted_reports = sorted(reports, key=lambda r: r.total_score, reverse=True)

    # 生成Markdown
    lines = [
        f"# SEO批量分析汇总报告",
        f"",
        f"**分析目录**: `{base_dir}`  ",
        f"**文件总数**: {total}  ",
        f"**平均分数**: {avg_score:.1f}/100  ",
        f"",
        f"## 分数分布",
        f"",
        f"| 等级 | 分数范围 | 文件数 | 占比 |",
        f"|------|---------|--------|------|",
        f"| 优秀 | 85-100 | {excellent} | {excellent/total*100:.1f}% |",
        f"| 良好 | 70-84 | {good} | {good/total*100:.1f}% |",
        f"| 中等 | 50-69 | {medium} | {medium/total*100:.1f}% |",
        f"| 较差 | 0-49 | {poor} | {poor/total*100:.1f}% |",
        f"",
        f"## 详细列表",
        f"",
        f"| 文件 | 总分 | 元数据 | 结构 | 关键词 | AI |",
        f"|------|------|--------|------|--------|-----|",
    ]

    for report in sorted_reports:
        rel_path = Path(report.file_path).relative_to(base_dir)
        score_emoji = "🟢" if report.total_score >= 70 else "🟡" if report.total_score >= 50 else "🔴"
        lines.append(
            f"| {score_emoji} `{rel_path}` | **{report.total_score:.1f}** | "
            f"{report.metadata_score:.1f} | {report.structure_score:.1f} | "
            f"{report.keyword_score:.1f} | {report.ai_score:.1f} |"
        )

    return "\n".join(lines)


if __name__ == '__main__':
    exit(main())
