import smartpy as sp

class playground(sp.Contract):
    def __init__(self):
        # storage block of variables 
        self.init(
            num_1 = sp.nat(5),
            num_2 = sp.int(-2),
            admin = sp.address("tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx"),
            time = sp.timestammp(sp.now()),
            map_1 = sp.map(l = {}, tkey = sp.TNat, tvalue = sp.TAddress),
            map_2 = sp.big_map(l = {}, tkey = sp.TNat, tvalue = sp.TAddress)
        )

        @sp.entry_point
        def change_num_values(self, params):
            sp.set_type(params, sp.TRecord(num_a=sp.TNat, num_b=sp.TInt))  