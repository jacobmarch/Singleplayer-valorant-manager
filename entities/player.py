from .team import Team

class Player:
    def __init__(self, 
                    first_name: str, 
                    last_name: str, 
                    age: int, 
                    role: str, 
                    nationality: str, 
                    nickname: str, 
                    team: Team = None
                ):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.nickname = nickname
        self.role = role
        self.nationality = nationality
        self.team = team
        self.contract_expiry = None
        self.salary = 0
        self.value = 0
        self.injured = False
        self.suspended = False