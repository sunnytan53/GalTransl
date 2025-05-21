from bert_score import score
import torch
from flask import Flask, request, jsonify # 新增导入

app = Flask(__name__) # 新增 Flask 应用实例

def calculate_bert_score(candidates, references, model_type='bert-base-chinese'):
    """
    计算BERTScore指标
    
    Args:
        candidates: 待评估的翻译列表
        references: 参考译文列表
        model_type: BERT模型类型，默认使用bert-base-chinese
        
    Returns:
        P: 精确率
        R: 召回率
        F1: F1分数
    """
    # 确保输入为列表
    if isinstance(candidates, str):
        candidates = [candidates]
    if isinstance(references, str):
        references = [references]
        
    # 设置设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 计算BERTScore
    P, R, F1 = score(
        cands=candidates, 
        refs=references,
        model_type=model_type,
        device=device,
        rescale_with_baseline=True,
        lang="zh"  # 指定中文语言
    )
    
    return P, R, F1

@app.route('/bert_score', methods=['POST']) # 新增 API 路由
def bert_score_api():
    data = request.get_json()
    if not data or 'candidates' not in data or 'references' not in data:
        return jsonify({"error": "Please provide 'candidates' and 'references' in JSON body"}), 400

    candidates = data['candidates']
    references = data['references']
    model_type = data.get('model_type', 'bert-base-chinese')

    try:
        P, R, F1 = calculate_bert_score(candidates, references, model_type)
        
        results = []
        for i, (p, r, f1) in enumerate(zip(P.tolist(), R.tolist(), F1.tolist())):
            results.append({
                "sentence": i + 1,
                "Precision": round(p, 4),
                "Recall": round(r, 4),
                "F1": round(f1, 4)
            })
        
        # print best and worst
        best = max(results, key=lambda x: x['F1'])
        worst = min(results, key=lambda x: x['F1'])
        print("Best sentence:")
        print(f"Sentence: {candidates[best['sentence'] - 1]}")
        print(f"F1: {best['F1']}")
        print("Worst sentence:")
        print(f"Sentence: {candidates[worst['sentence'] - 1]}")
        print(f"F1: {worst['F1']}")
        print("---")
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# 使用示例
if __name__ == "__main__":
    
    # 启动 Flask 开发服务器
    app.run(debug=True, host='0.0.0.0', port=5000) # 修改为运行 Flask 应用
    
