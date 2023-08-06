from oe_utils.data.models import Wijziging, WijzigingBase, Base

class Bla(WijzigingBase, Base):
    # __tablename__ = 'wijzigingshistoriek_test'
    pass

ar = Bla()
# print(ar.__tablename__)

print('test')