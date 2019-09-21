


from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth.base_user import BaseUserManager
from abc import ABCMeta, abstractmethod

# 試しにメールアドレスでのログイン機能を実装するためのコードを書いてみる
class UserManager(BaseUserManager):
    """ユーザーマネージャー"""

    user_in_migrations = True

    def _create_user(self, mail_address, password, **extra_fields):
        """メールアドレスの登録を必須にする"""
        if not mail_address:
            raise ValueError('The given email must be set')
        email = self.normalize_email(mail_address)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mail_address, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(mail_address, password, **extra_fields)

    def create_superuser(self, mail_address, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mail_address, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    ユーザ情報を提供するDTOクラス
    """
    user_id = models.IntegerField(_('ユーザID'), primary_key=True)
    username = models.CharField(_('ユーザ名'), max_length=40, default=None, blank=True)
    mail_address = models.EmailField(_('メールアドレス'), unique=True, default=None)
    password = models.CharField(_('パスワード'), max_length=10, default=None) #パスワードの入力制限は設けるか

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    EMAIL_FIELD = 'mail_address'
    USERNAME_FIELD = 'mail_address'
    REQUIRED_FIELDS = []

    def check_pass(self, password: str) -> bool:
        """引数のパスワードとユーザーインスタンスのパスワードが一致するかチェックする

        :param password: 画面入力されたパスワード
        :return: 引数のパスワードとユーザーインスタンスが持つパスワードが一致するかどうかチェックする
        """
        user = UserDao.get_user(str(self.user_id))
        if user is not None:
            return password == user.password
        return False



class UserDao:
    """Userオブジェクトを操作するクラス"""

    @staticmethod
    def get_user(user_id: int) -> User:
        """Userオブジェクトを取得

        :param mail_address メールアドレス
        """
        try:
            return User.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            print("対象のオブジェクトがDBに存在しません")

    @staticmethod
    def get_users():
        return User.objects.order_by('username')

    @staticmethod
    def create_user(user_id:int, username:str, mail_address:str, password:str):
        user = User()
        user.user_id = user_id
        user.username = username
        user.mail_address = mail_address
        user.password = password
        user.save()

    @staticmethod
    def delete_user_by_user_id(user_id: int):
        """ユーザIDに紐づくユーザを削除する"""
        User.objects.filter(user_id=user_id).delete()

    @staticmethod
    def test_session():
        return Session.objects.all()

class Lottery_pool(models.Model):
    """
    抽選申込情報を提供するDTOクラス
    """
    reservation_id =models.AutoField(_('予約ID'), primary_key=True)
    user_id = models.IntegerField(_('ユーザID'))
    username = models.CharField(_('ユーザ名'), max_length=40)
    check_in_date = models.DateField(_('チェックイン日'))
    check_out_date = models.DateField(_('チェックアウト日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'))
    number_of_guests = models.SmallIntegerField(_('宿泊人数'))
    priority = models.SmallIntegerField(_('希望') ,default=1)
    purpose = models.CharField(_('利用形態'), max_length=10, default=None)

class LotDao:
    """Lottery_poolオブジェクトを操作するクラス"""

    @staticmethod
    def create_res_by_in_and_out(user_id: int, check_in_date: datetime.date, check_out_date: datetime.date, number_of_rooms: int, number_of_guests: int, purpose: str):
        # TODO: 文字のベタ打ちを直す
        lot = Lottery_pool()
        lot.user_id = user_id
        lot.username = UserDao.get_user(user_id).username
        lot.check_in_date = check_in_date
        lot.check_out_date = check_out_date
        lot.number_of_rooms = number_of_rooms
        lot.number_of_guests = number_of_guests
        lot.purpose = purpose
        lot.request_status = 1
        lot.expire_date = datetime.date.today() + datetime.timedelta(days=31)
        lot.save()

        # 滞在日数を導出
        visit_duration = (check_out_date - check_in_date).days

        # 宿泊データを作成
        LodginDao.create_lodging_data(lot.reservation_id, lot.user_id, check_in_date , visit_duration)

    @staticmethod
    def get_res_list(user_id: int) -> list:
        """Lotteryオブジェクトを取得

        :param user_id ユーザID
        """
        return Lottery_pool.objects.filter(user_id=user_id)

    @staticmethod
    def get_res_by_reservation_id(reservation_id:int):
        """Lotteryオブジェクトを取得

        :param reservation_id 予約ID
        """
        return Lottery_pool.objects.get(reservation_id=reservation_id)

    @staticmethod
    def delete_by_reservation_id(reservation_id: int):
        """Lotteryオブジェクトを削除"""
        Lottery_pool.objects.filter(reservation_id=reservation_id).delete()

    @staticmethod
    def delete_by_user_id(user_id: int):
        """Lotteryオブジェクトを削除"""
        Lottery_pool.objects.filter(user_id=user_id).delete()


class Reservations(models.Model):
    """
    予約情報を提供するDTOクラス
    """
    reservation_id = models.IntegerField(_('予約ID'), primary_key=True)
    user_id = models.IntegerField(_('ユーザID'))
    username = models.CharField(_('ユーザ名'), max_length=40)
    check_in_date = models.DateField(_('チェックイン日'))
    check_out_date = models.DateField(_('チェックアウト日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'))
    number_of_guests = models.SmallIntegerField(_('宿泊人数'))
    purpose = models.CharField(_('利用形態'), max_length=10, default=None)
    lottery_flag = models.BooleanField(_('抽選フラグ'), default=True)
    request_status = models.SmallIntegerField(_('申込ステータス'))
    expire_date = models.DateField(_('有効期限'))

class ResDao:
    """Reservationsオブジェクトを操作するクラス"""

    @staticmethod
    def create_res_by_in_and_out(user_id: int, check_in_date: datetime.date, check_out_date: datetime.date, number_of_rooms: int, number_of_guests: int, purpose: str):
        # TODO: 文字のベタ打ちを直す　→ 直接予約情報作成は使わない削除予定
        res = Reservations()
        res.user_id = user_id
        res.username = UserDao.get_user(user_id).username
        res.check_in_date = check_in_date
        res.check_out_date = check_out_date
        res.number_of_rooms = number_of_rooms
        res.number_of_guests = number_of_guests
        res.purpose = purpose
        res.request_status = 1
        res.expire_date = datetime.date.today() + datetime.timedelta(days=31)
        res.save()

        # 滞在日数を導出
        visit_duration = (check_out_date - check_in_date).days

        # 宿泊データを作成
        LodginDao.create_lodging_data(res.reservation_id, res.user_id, check_in_date , visit_duration)

    @staticmethod
    def create_res_by_lottery(reservation_id: int):
        """抽選情報から予約情報を作成する"""
        lot = LotDao.get_res_by_reservation_id(reservation_id)

        res = Reservations()
        res.reservation_id = lot.reservation_id
        res.user_id = lot.user_id
        res.username = UserDao.get_user(lot.user_id).username
        res.check_in_date = lot.check_in_date
        res.check_out_date = lot.check_out_date
        res.number_of_rooms = lot.number_of_rooms
        res.number_of_guests = lot.number_of_guests
        res.purpose = lot.purpose
        res.request_status = 1
        res.expire_date = datetime.date.today() + datetime.timedelta(days=31)
        res.save()

    @staticmethod
    def delete_by_reservation_id(reservation_id: int):
        """Lotteryオブジェクトを削除"""
        Reservations.objects.filter(reservation_id=reservation_id).delete()

    @staticmethod
    def delete_by_user_id(user_id: int):
        """Lotteryオブジェクトを削除"""
        Reservations.objects.filter(user_id=user_id).delete()

    @staticmethod
    def get_res_list(user_id: int) -> list:
        """ユーザIDに紐づくReservationオブジェクトを取得

        :param mail_address メールアドレス
        """
        return Reservations.objects.filter(user_id=user_id)

    @staticmethod
    def get_res_by_year_and_month(year:int, month:int):
        """引数の年月に紐づく予約情報を取得する"""
        return Reservations.objects.filter(check_in_date__year=year).filter(check_in_date__month=month)

    @staticmethod
    def get_res():
        """ユーザ情報でソートした予約情報を取得する"""
        return Reservations.objects.order_by('username')

    @staticmethod
    def get_res_by_month(month: int) -> Reservations:
        """
        引数の月度に該当する予約を取り出す
        :param month: 対象月度
        :return: 対象月度に該当するReservationsクラス
        """
        return Reservations.objects.filter(check_in_date__range=month)

    def del_res_by_month(month: int):
        """
        引数の月度の予約情報を削除する
        :param month:対象月度
        :return:
        """
        pass

class Lodging(models.Model):
    """宿泊日数情報を提供するDTOクラス(予約クラスの子クラス)"""
    reservation_id = models.IntegerField(_('予約ID'))
    user_id = models.IntegerField(_("ユーザID"))
    lodging_date = models.DateField(_('宿泊日'))

class LodginDao:

    @staticmethod
    def get_lodging_by_reservation_id(reservation_id:int):
        """予約IDに紐づく宿泊エンティティのQuerySetを返却"""
        return Lodging.objects.filter(reservation_id=reservation_id)

    @staticmethod
    def create_lodging_data(reservation_id: int, user_id: int, check_in_date: datetime.date , visit_duration: int):
        """予約エンティティと滞在日数を元に、宿泊エンティティを新規作成"""

        for vis_day in range(visit_duration):
            lodging = Lodging()
            lodging.user_id = user_id
            lodging.reservation_id = reservation_id
            lodging.lodging_date = check_in_date + datetime.timedelta(days=vis_day)
            lodging.save()

    @staticmethod
    def delete_by_reservation_id(reservation_id: int):
        """Lodgingオブジェクトを削除"""
        Lodging.objects.filter(reservation_id=reservation_id).delete()

    @staticmethod
    def delete_by_user_id(user_id: int):
        """Lotteryオブジェクトを削除"""
        Lodging.objects.filter(user_id=user_id).delete()
