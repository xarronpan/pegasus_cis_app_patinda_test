import libs.app.root.llm
import libs.app.types as types
import libs.util.util
from .. import config

class Application(libs.app.root.llm.Application):
    def __init__(self):
         libs.app.root.llm.Application.__init__(
             self, config.appid, config.locale)

    def get_hided_fields(self):
        return ["price", "total",
                "supplier", "currency", "uninvoiced_qty",
                "invoice_number", "vendor", "invoice_date", "payment_term", "due_date"]

    def get_extract_method(self):
        return "llm"

    def ai_header_fields(self):
        return []

    def ai_line_fields(self):
        return [{"name": "product_name",
                 "llm_name": "商品名称"},
                {"name": "specification",
                 "llm_name": "规格"},
                {"name": "color",
                 "llm_name": "颜色"},
                {"name": "quantity",
                 "llm_name": "数量"},
                {"name": "order_id",
                 "llm_name": "订单号"},
                {"name": "note",
                 "llm_name": "备注"}]

    def order_line_extention_keys(self) -> list[str]:
        return ["color", "note"]

    def get_web_config(self) -> dict:
        return {
            "order_line_extention_names": {"color": "颜色", "note": "备注"}
        }

    def match_order_line(self, ctx: dict, header: types.Header, recognized_row: types.Row) \
        -> tuple[ str|None, # result
                  dict|None, # diagnose
                  list[types.MatchedOrderLine] ]:

        if (recognized_row["extentions"]["product_name"] == "" and
            recognized_row["extentions"]["order_id"] == ""):
            return None, None, []

        order_line = {}
        order_line["order_id"] = recognized_row["order_id"]
        order_line["product_id"] = recognized_row["extentions"]["product_name"]
        order_line["desc"] = recognized_row["extentions"]["specification"]
        order_line["price"] = 0
        order_line["quantity"] = recognized_row["quantity"]
        order_line["total"] = 0
        order_line["email_id"] = recognized_row["email_id"]
        order_line["filename"] = recognized_row["filename"]
        order_line["sheet"] = recognized_row["sheet"]
        order_line["supplier"] = ""
        order_line["currency"] = ""
        order_line["match_detail"] = ""
        order_line["extentions"] = {}
        order_line["extentions"]["color"] = recognized_row["extentions"]["color"]
        order_line["extentions"]["note"] = recognized_row["extentions"]["note"]

        return "succ", None, [order_line]

    def ai_prompts(self):
        return {
            "tools_fun_nam": "extract_fields_from_document",
            "tools_fun_prompt": "提取工厂计件单中的字段. 若字段不存在，则填空字符串",
            "sys_prompt": "你是一位工厂计件单处理专家。你了解工厂计件单处理的所有要求",
            "msg_prompt": "请从工厂计件单处中抽取信息, 将相关参数填入extract_fields_from_document。填入的参数，严格遵循extract_fields_from_document中的参数格式。其中参数Po Number是订单号"
        }
