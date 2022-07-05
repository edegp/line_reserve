import logging
import json
import os
from common import common_const, utils
from validation.restaurant_param_check import RestaurantParamCheck
from restaurant.restaurant_shop_reservation import RestaurantShopReservation
from restaurant.restaurant_reservation_info import RestaurantReservationInfo

CHANNEL_ID = os.getenv("OA_CHANNEL_ID")
LIFF_CHANNEL_ID = os.getenv("LIFF_CHANNEL_ID")

# ログ出力の設定
LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL")
logger = logging.getLogger()
if LOGGER_LEVEL == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# テーブル操作クラスの初期化
shop_reservation_table_controller = RestaurantShopReservation()
reservation_info_table_controller = RestaurantReservationInfo()


def delete_reservation_time(shop_name, user_id, reservation_date, time):
    """
    予約済み時間の情報を取得する

    Parameters
    ----------
    shop_id : str
        予約する店舗のID
    preferred_day : str
        予約する日付

    Returns
    -------
    day_reserved_info_list: list of dict
        指定日の時間毎の予約情報

    Notes
    -------
    指定日に予約がない場合、空のリストを返す
    """
    # 指定日の予約情報を取得
    key1 = {
        "shop_name": shop_name,
        "user_id": user_id,
        "reservation_date": reservation_date,
        "reservation_starttime": time,
    }
    # 指定日の予約情報を取得
    key2 = {
        "shop_name": shop_name,
        "user_id": user_id,
        "reserved_day": reservation_date,
        "reservation_starttime": time,
    }
    day_reserved_info1 = shop_reservation_table_controller.delete_item(**key1)
    day_reserved_info2 = reservation_info_table_controller.delete_item(**key2)

    # 指定日の予約がない場合空のリストを返す
    if not day_reserved_info1| not day_reserved_info2:
        return []

    return day_reserved_info1, day_reserved_info2


def lambda_handler(event, context):
    """
    DynamoDBテーブルから日ごとの予約情報一覧を取得して返却する

    Parameters
    ----------
    event : dict
        フロントから送られたパラメータ等の情報
    context : __main__.LambdaContext
        Lambdaランタイムや関数名等のメタ情報

    Returns
    -------
    response: dict
        正常の場合、予約情報を返却する。
        エラーの場合、エラーコードとエラーメッセージを返却する。
    """
    logger.info(event)

    if event["body"] is None:
        error_msg_disp = common_const.const.MSG_ERROR_NOPARAM
        return utils.create_error_response(error_msg_disp, 400)
    body = json.loads(event["body"])
    # ユーザーID取得
    try:
        user_profile = line.get_profile(body["idToken"], LIFF_CHANNEL_ID)
        if (
            "error" in user_profile and "expired" in user_profile["error_description"]
        ):  # noqa 501
            return utils.create_error_response("Forbidden", 403)
        else:
            body["userId"] = user_profile["sub"]

    except Exception:
        logger.exception("不正なIDトークンが使用されています")
        return utils.create_error_response("Error")

    # パラメータチェック
    param_checker = RestaurantParamCheck(body)
    if error_msg := param_checker.check_api_reservation_delete():
        error_msg_disp = ("\n").join(error_msg)
        logger.error(error_msg_disp)
        return utils.create_error_response(error_msg_disp, status=400)  # noqa: E501

    try:
        day_reserved_list = delete_reservation_time(
            body["shopName"],
            body["userId"],
            body["reservationDate"],
            body["reservationStarttime"],
        )
    except Exception as e:
        logger.exception("Occur Exception: %s", e)
        return utils.create_error_response("ERROR")

    return utils.create_success_response(
        json.dumps(day_reserved_list, default=utils.decimal_to_int, ensure_ascii=False)
    )
