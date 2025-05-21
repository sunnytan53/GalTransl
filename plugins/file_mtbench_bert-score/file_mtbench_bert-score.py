import orjson, re
import os
import torch
from GalTransl import LOGGER
from GalTransl.GTPlugin import GFilePlugin
from .bert_score_server import calculate_bert_score


class file_plugin(GFilePlugin):
    def gtp_init(self, plugin_conf: dict, project_conf: dict):
        """
        This method is called when the plugin is loaded.在插件加载时被调用。
        :param plugin_conf: The settings for the plugin.插件yaml中所有设置的dict。
        :param project_conf: The settings for the project.项目yaml中common下设置的dict。
        """
        self.all_stats = {"P": [], "R": [], "F1": []}  # 存储所有句子的统计数据
        self.file_stats = {}  # 按文件存储统计数据
        self.line_count = 0
        self.model_type = plugin_conf.get("model_type", "bert-base-chinese")  # 默认使用bert-base-chinese模型
        pass                                          

    def load_file(self, file_path: str) -> list:
        """
        This method is called to load a file.
        加载文件时被调用。
        :param file_path: The path of the file to load.文件路径。
        :return: A list of objects with message and name(optional).返回一个包含message和name(可空)的对象列表。
        """
        if not file_path.endswith(".json"):
            # 检查不支持的文件类型并抛出TypeError
            raise TypeError("请检查filePlugin的配置并选择合适的文件插件.")
        with open(file_path, "r", encoding="utf-8") as f:
            json_list = orjson.loads(f.read())
        return json_list

    def save_file(self, file_path: str, transl_json: list):
        """
        This method is called to save a file.
        保存文件时被调用。
        :param file_path: The path of the file to save.保存文件路径
        :param transl_json: A list of objects same as the return of load_file().load_file提供的json在翻译message和name后的结果。
        :return: None.
        """
        candidates = []
        references = []
        valid_items = []
        
        # 收集该文件所有句子的统计数据
        for item in transl_json:
            message = item.get('message', '')
            ref = item.get('ref', '')
            if not message or not ref:
                continue
            message = message.replace("\n", "").replace("\r", "")
            ref = ref.replace("\n", "").replace("\r", "")
            candidates.append(message)
            references.append(ref)
            valid_items.append(item)
        
        if candidates and references:
            # 计算BERT-Score
            try:
                P, R, F1 = calculate_bert_score(candidates, references, self.model_type)
                
                # 将PyTorch张量转换为Python列表
                P_list = P.tolist()
                R_list = R.tolist()
                F1_list = F1.tolist()
                
                # 为每个句子添加分数
                for i, item in enumerate(valid_items):
                    item['bert_score'] = {
                        "P": round(P_list[i], 4),
                        "R": round(R_list[i], 4),
                        "F1": round(F1_list[i], 4)
                    }
                
                # 存储文件统计数据
                self.file_stats[file_path] = {
                    "P": P_list,
                    "R": R_list,
                    "F1": F1_list
                }
                
                # 更新总体统计数据
                self.all_stats["P"].extend(P_list)
                self.all_stats["R"].extend(R_list)
                self.all_stats["F1"].extend(F1_list)
                self.line_count += len(valid_items)
            except Exception as e:
                LOGGER.error(f"[BERT-Score翻译评估] 计算BERT-Score时出错: {str(e)}")
        
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(transl_json, option=orjson.OPT_INDENT_2))

    def gtp_final(self):
        """
        This method is called after all translations are done.
        在所有文件翻译完成之后的动作，例如输出提示信息。
        """
        # 输出每个文件的BERT-Score分数
        for file_path, stats in self.file_stats.items():
            if stats["F1"]:
                file_name = os.path.basename(file_path)
                avg_p = sum(stats["P"]) / len(stats["P"]) if stats["P"] else 0
                avg_r = sum(stats["R"]) / len(stats["R"]) if stats["R"] else 0
                avg_f1 = sum(stats["F1"]) / len(stats["F1"]) if stats["F1"] else 0
                LOGGER.info(f"[BERT-Score翻译评估] {file_name} 的 BERT-Score 分数 - P: {avg_p:.4f}, R: {avg_r:.4f}, F1: {avg_f1:.4f}")
        
        # 输出总体BERT-Score分数
        if self.all_stats["F1"]:
            total_p = sum(self.all_stats["P"]) / len(self.all_stats["P"]) if self.all_stats["P"] else 0
            total_r = sum(self.all_stats["R"]) / len(self.all_stats["R"]) if self.all_stats["R"] else 0
            total_f1 = sum(self.all_stats["F1"]) / len(self.all_stats["F1"]) if self.all_stats["F1"] else 0
            LOGGER.info(f"[BERT-Score翻译评估] 总体 BERT-Score 分数 - P: {total_p:.4f}, R: {total_r:.4f}, F1: {total_f1:.4f}")
            LOGGER.info(f"[BERT-Score翻译评估] 共评估了 {self.line_count} 个句子")


