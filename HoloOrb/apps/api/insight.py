from flask import request, current_app
from flask_jwt_extended import jwt_required
from apps.common.response import success, error
from apps.api import insight_bp
from apps.models.models import Device, Metric


def _build_device_context() -> str:
    """查询设备信息和最近50条监控指标并组装为上下文文本"""
    parts = []

    # 设备清单
    devices = Device.query.all()
    if devices:
        lines = ["=== 当前系统设备清单 ==="]
        for d in devices:
            lines.append(
                f"- [{d.status}] {d.name}（IP: {d.ip}）"
                f" | 类型: {d.type}"
                f" | 区域: {d.area or '未分配'}"
                f" | 温度: {d.temperature or 'N/A'}"
                f" | 运行时长: {d.uptime or 'N/A'}"
                f" | 接口: {d.in_use_interfaces}/{d.interfaces}"
                f"{' | ' + d.description if d.description else ''}"
            )
        parts.append("\n".join(lines))
    else:
        parts.append("当前系统暂无设备信息。")

    # 最近50条监控指标
    recent_metrics = Metric.query.order_by(Metric.collected_at.desc(), Metric.id.desc()).limit(50).all()
    if recent_metrics:
        lines = ["\n=== 最近50条监控指标 ==="]
        for m in recent_metrics:
            device_name = m.device.name if m.device else f"设备ID:{m.device_id}"
            lines.append(
                f"- [{m.collected_at.strftime('%Y-%m-%d %H:%M:%S') if m.collected_at else 'N/A'}] "
                f"{device_name}"
                f" | CPU: {m.cpu:.1f}%"
                f" | 内存: {m.memory:.1f}%"
                f" | 入流量: {m.traffic_in:.1f}Mbps"
                f" | 出流量: {m.traffic_out:.1f}Mbps"
            )
        parts.append("\n".join(lines))

    return "\n".join(parts)


@insight_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return error('缺少消息内容', http_status=400)

        api_key = current_app.config.get('DEEPSEEK_API_KEY')
        base_url = current_app.config.get('DEEPSEEK_API_BASE_URL')
        model = current_app.config.get('DEEPSEEK_MODEL')

        if not api_key:
            return error('DeepSeek API Key 未配置', http_status=500)

        # 构建系统提示词，附带设备信息和监控指标作为上下文
        device_context = _build_device_context()
        system_content = (
            "你是 HoloOrb 智能运维助手，专业负责设备监控、告警分析、网络健康度评估。"
            "请以清晰、结构化的方式回答用户的问题，包括分析结论和建议。\n\n"
            f"{device_context}"
        )
        system_msg = {"role": "system", "content": system_content}

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)

        history = data.get('history', [])
        messages = [system_msg] + history + [{"role": "user", "content": data['message']}]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )

        content = response.choices[0].message.content
        return success({'content': content})

    except Exception as e:
        current_app.logger.error(f'DeepSeek API 调用失败: {str(e)}')
        return error(f'AI 服务调用失败: {str(e)}', http_status=500)