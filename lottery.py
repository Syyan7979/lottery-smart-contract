import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self, _admin):
        self.init(
            players = sp.map(l = {}, tkey = sp.TNat, tvalue = sp.TAddress),
            ticket_cost = sp.tez(1),
            ticket_available = sp.nat(5),
            max_tickets = sp.nat(5),
            admin = _admin
        )
    
    @sp.entry_point
    def buy_ticket(self, num_tickets):
        sp.set_type(num_tickets, sp.TNat)

        # Local variables
        iter_ceil = sp.local("iter_ceil", self.data.max_tickets)

        # Assertions
        sp.verify(num_tickets > 0, message = "Must buy at least 1 ticket")
        sp.verify(sp.utils.mutez_to_nat(sp.amount) == sp.utils.mutez_to_nat(self.data.ticket_cost) * num_tickets, message = "tez amount must be equal to ticket cost (1 tez)")
        
        # Update storage
        # check if num_tickets is greater than ticket_availabl; if it is return extra tez to sender
        sp.if num_tickets > self.data.ticket_available:
            extra_balance = sp.amount - sp.utils.nat_to_mutez(sp.utils.mutez_to_nat(self.data.ticket_cost) * self.data.ticket_available)
            sp.send(sp.sender, extra_balance)
            iter_ceil.value = self.data.ticket_available
        sp.else:
            iter_ceil.value = num_tickets
        sp.for i in sp.range(0, iter_ceil.value):
            self.data.players[sp.len(self.data.players)] = sp.sender
        self.data.ticket_available = sp.as_nat(self.data.ticket_available - iter_ceil.value)

    @sp.entry_point
    def draw_winner(self, random_number):
        sp.set_type(random_number, sp.TNat)

        # Assertions
        sp.verify(sp.sender == self.data.admin, message = "Not Authorized: Only admin can draw winner")
        sp.verify(self.data.ticket_available == 0, message = "All tickets must be sold")

        # Update storage
        winner_index = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_index]

        # Send tez to winner
        sp.send(winner_address, sp.balance)

        # Reset storage
        self.data.players = {}
        self.data.ticket_available = self.data.max_tickets
    
    @sp.entry_point
    def update_ticket_cost(self, new_cost):
        sp.set_type(new_cost, sp.TMutez)

        # Assertions
        sp.verify(sp.sender == self.data.admin, message = "Not Authorized: Only admin can update ticket cost")
        sp.verify(new_cost > sp.mutez(0), message = "Ticket cost must be greater than 0")
        sp.verify(self.data.ticket_available == self.data.max_tickets, "No tickets must be sold before updating ticket cost")

        # Update storage
        self.data.ticket_cost = new_cost

    @sp.entry_point
    def update_max_tickets(self, new_max):
        sp.set_type(new_max, sp.TNat)

        # Assertions
        sp.verify(sp.sender == self.data.admin, message = "Not Authorized: Only admin can update ticket cost")
        sp.verify(new_max > 0, message = "Max tickets must be greater than 0")
        sp.verify(self.data.ticket_available == self.data.max_tickets, "No tickets must be sold before updating max tickets")

        # Update storage
        self.data.max_tickets = new_max
        self.data.ticket_available = new_max

    @sp.entry_point
    def default(self):
        sp.send(sp.sender, sp.balance)


@sp.add_test(name = "Lottery")
def test():
    scenario = sp.test_scenario()

    # Test Accounts
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    kurt = sp.test_account("Kurt")
    mark = sp.test_account("Mark")
    admin = sp.test_account("Admin")

    # lottery instance
    lottery = Lottery(admin.address)
    scenario += lottery

    # Alice buys 3 tickets
    scenario += lottery.buy_ticket(3).run(sender = alice, amount = sp.tez(3))

    # Bob buys 2 tickets
    scenario += lottery.buy_ticket(3).run(sender = bob, amount = sp.tez(3))

    # admin draws winner
    scenario += lottery.draw_winner(1659).run(sender = admin)

    # eve buys 1 ticket
    scenario += lottery.buy_ticket(1).run(sender = eve, amount = sp.tez(1))

    #kurt buys 1 ticket
    scenario += lottery.buy_ticket(1).run(sender = kurt, amount = sp.tez(1))

    # mark buys 1 ticket
    scenario += lottery.buy_ticket(1).run(sender = mark, amount = sp.tez(1))

     # admin draws winner
    scenario += lottery.draw_winner(1659).run(sender = admin, valid = False) # should fail because all tickets are not sold

    # Alice buys 1 ticket
    scenario += lottery.buy_ticket(1).run(sender = alice, amount = sp.tez(1))

    # Bob buys 1 ticket
    scenario += lottery.buy_ticket(1).run(sender = bob, amount = sp.tez(1))

    # admin changes ticket cost to 2 tez
    scenario += lottery.update_ticket_cost(sp.tez(2)).run(sender = admin, valid = False) # should fail because number of tickets sold is not equal to 0

    # admin draws winner
    scenario += lottery.draw_winner(1659).run(sender = admin)

    # admin changes ticket cost to 2 tez
    scenario += lottery.update_ticket_cost(sp.tez(2)).run(sender = admin)

    # admin changes max tickets to 10
    scenario += lottery.update_max_tickets(10).run(sender = admin)

    # Alice buys 9 tickets
    scenario += lottery.buy_ticket(9).run(sender = alice, amount = sp.tez(18))

    # admin changes max tickets to 20
    scenario += lottery.update_max_tickets(20).run(sender = admin, valid = False) # should fail because number of tickets sold is not equal to 0

    # bob buys 1 ticket
    scenario += lottery.buy_ticket(1).run(sender = bob, amount = sp.tez(2))

    # admin draws winner
    scenario += lottery.draw_winner(1659).run(sender = admin)