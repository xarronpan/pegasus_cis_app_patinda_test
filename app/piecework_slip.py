import libs.app.packing_list.base as base
import libs.app.types as types
import pandas as pd
import re
from .. import config

_MAX_PRICE_ERROR = 0.003

class Application(base.Application):
    def __init__(self):
        cfg = {}
        cfg["check_status"] = config.check_status
        cfg["check_received"] = False
        cfg["sync_invoice_with_approval"] = config.sync_invoice_with_approval
        base.Application.__init__(self, config.appid, config.locale, cfg)

    def get_product_ids(self, val):
        product_ids = set()
        if pd.isna(val):
            return []

        if isinstance(val, (int)):
            val = str(val)
        if isinstance(val, (float)):
            val = str(int(val))

        val = str(val)

        val = val.replace("\n", "")
        val = val.replace("\r", "")

        product_id_strs = re.findall(r'\S+', val)
        product_ids |= set(product_id_strs)

        return list(product_ids)

    def get_order_ids(self, val):
        order_ids = set()
        if pd.isna(val):
            return []

        if isinstance(val, (int)):
            val = str(val)
        if isinstance(val, (float)):
            val = str(int(val))

        val = str(val)

        order_id_strs = re.findall(r'\S+', val)
        order_ids |= set(order_id_strs)
        return list(order_ids)

    def match_header(self, ctx: dict, header: types.Header, raw_header: dict[str, str]):
        header["extentions"]["po_number"] = raw_header.get("po_number", "")
        return header

    def match_order_line(self, ctx: dict, header: types.Header, recognized_row: types.Row) \
        -> tuple[ str|None, # result
                  dict|None, # diagnose
                  list[types.MatchedOrderLine] ]:

        if recognized_row["order_id"] == "":
            recognized_row["order_id"] = header["extentions"]["po_number"]

        result, diagnose, order_line_list = super().match_order_line(ctx, header, recognized_row)
        return result, diagnose, order_line_list

    def check_order_line(self, ctx: dict, header: types.Header, order_line: types.OrderLine, options: str) \
        -> tuple[ str,  # result
                  str   # diagnose
                ]:

        return "succ", ""

    def ai_prompts(self):
        return {
            "tools_fun_nam": "extract_fields_from_document",
            "tools_fun_prompt": "提取工厂计件单中的字段. 若字段不存在，则填空字符串",
            "sys_prompt": "你是一位工厂计件单处理专家。你了解工厂计件单处理的所有要求",
            "msg_prompt": "请从工厂计件单处中抽取信息, 将相关参数填入extract_fields_from_document。填入的参数，严格遵循extract_fields_from_document中的参数格式。其中参数Po Number是订单号"
        }

    def ai_based_only(self):
        return True

    def ai_header_fields(self):
        return [{"name": "po_number",
                 "llm_name": "Po Number"}]

    def ai_line_fields(self):
        return [{"name": "product_id",
                 "llm_name": "Product",
                 "desc": "商品名称"}]

    def get_web_config(self) -> dict:
        return {
            "header_extention_names": {
                "po_number": "订单号"
            },
        }
