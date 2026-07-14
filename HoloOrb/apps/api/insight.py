from flask import request, current_app
from flask_jwt_extended import jwt_required
from apps.common.response import success, error
from apps.api import insight_bp


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

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)

        system_msg = {
            "role": "system",
            "content": "你是 HoloOrb 智能运维助手，专业负责设备监控、告警分析、网络健康度评估。请以清晰、结构化的方式回答用户的问题，包括分析结论和建议。"
        }

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