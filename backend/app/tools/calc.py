"""Tính biểu thức số học bằng Decimal. Chỉ nhận số thập phân, + - * /, ngoặc và dấu âm; không thực thi mã do model sinh."""
import ast
from decimal import Decimal, DecimalException, ROUND_HALF_UP, getcontext

getcontext().prec = 34

_OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b}


class CalcError(ValueError):
    pass


def evaluate(expression: str) -> Decimal:
    if not isinstance(expression, str):
        raise CalcError("Biểu thức phải là chuỗi.")
    if len(expression) > 500:
        raise CalcError("Biểu thức quá dài.")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise CalcError(f"Biểu thức không hợp lệ: {expression!r}") from e
    value = _eval(tree.body, expression)
    if not value.is_finite():
        raise CalcError("Kết quả không hữu hạn.")
    return abs(value) if value.is_zero() else value  # không trả về -0


def _eval(node, source: str) -> Decimal:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        literal = ast.get_source_segment(source, node) or ""
        if literal[:2].lower() in ("0x", "0o", "0b"):
            raise CalcError(f"Chỉ nhận số thập phân: {literal}")
        return Decimal(literal.replace("_", ""))  # đọc từ văn bản gốc để không mất độ chính xác qua float
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _eval(node.operand, source)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left, source), _eval(node.right, source)
        try:
            return _OPS[type(node.op)](left, right)
        except (DecimalException, ZeroDivisionError) as e:
            raise CalcError("Phép tính không xác định (chia cho 0 hoặc tràn số).") from e
    raise CalcError(f"Không được phép dùng thành phần {type(node).__name__} trong biểu thức.")


def round_to(value: Decimal, step: int = 1) -> Decimal:
    """Làm tròn tới bội số của step (ví dụ step=1000 để làm tròn đến nghìn đồng)."""
    return (value / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * step
