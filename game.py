import random
from enum import Enum

class Role(Enum):
    Villager = 0
    Werewolf = 1
    Doctor = 2
    Seer = 3
    Unknown = 4

class Game(object):
    def __init__(self, numPlayers):
        self.Debug = False
        self.players = []
        self.numPlayers = numPlayers
        for i in range(0, numPlayers):
            self.players.append(AI(i, Role.Villager))
        random.shuffle(self.players)
        self.players[0].role = Role.Werewolf
        self.players[1].role = Role.Werewolf
        self.players[2].role = Role.Seer
        self.players[3].role = Role.Doctor
        random.shuffle(self.players)
    
    def Play(self):
        villagersWon = False
        werewolvesWon = False
        
        isNight = True
        while not villagersWon and not werewolvesWon:
            if isNight:
                self.Night()
            else:
                self.Day()
                
            isNight = not isNight
            
            villagersWon = self.HaveVillagersWon()
            werewolvesWon = self.HaveWerewolvesWon()
        
        if villagersWon:
            if self.Debug:
                print("The villagers have won!")
            return "Villager"
        else:
            if self.Debug:
                print("The werewolves have won!")
            return "Werewolf"
            
    
    def Night(self):
        # determine who should be saved
        mPersonToSaveID = -1
        for mPlayer in self.players:
            if mPlayer.role == Role.Doctor:
                mPersonToSaveID = mPlayer.Doctor()
        
        # now determine who the werewolves will kill
        random.shuffle(self.players)
        werewolfIDs = self.AliveWerewolves()
        werewolves = []
        for mPlayer in self.players:
            if mPlayer.role == Role.Werewolf and mPlayer.isAlive:
                werewolves.append(mPlayer)
                
        chosen = {}

        # while they don't agree, keep asking
        haveDecided = False
        while not haveDecided:
            mChosen = {}
            for mWere in werewolves:
                mChosen[mWere.playerID] = mWere.Werewolf(chosen)
            chosen = mChosen            

            mPersonToKillID = -1
            haveDecided = True
            for key, value in chosen.items():
                if mPersonToKillID == -1:
                    mPersonToKillID = value
                else:
                    if not value == mPersonToKillID:
                        haveDecided = False                
                
        if not mPersonToKillID == mPersonToSaveID:
            for mPlayer in self.players:
                if mPlayer.playerID == mPersonToKillID:
                    mPlayer.isAlive = False
                    if self.Debug:
                        print("Player #" + str(mPersonToKillID) + " (" + mPlayer.role.name + ") was killed in the night.")
        elif self.Debug:
            print("The doctor managed to save Player #" + str(mPersonToSaveID) + "!")
            
        # now determine whose role the Seer discovers
        for mPlayer in self.players:
            if mPlayer.role == Role.Seer:
                mPlayerToDiscover = mPlayer.Seer()
                for mPlayer2 in self.players:
                    if mPlayer2.playerID == mPlayerToDiscover:
                        mPlayer.Discover(mPlayerToDiscover, mPlayer2.role)
        
        # this is the end of the nighttime round
    
    def Day(self):
        self.votes = []
        for i in range(0, self.numPlayers):
            self.votes.append(0)
            
        for mPlayer in self.players:
            self.votes[mPlayer.Villager()] += 1
        
        for mPlayer in self.players:
            if mPlayer.playerID == self.votes.index(max(self.votes)):
                mPlayer.isAlive = False
                if self.Debug:
                    print("Player #" + str(mPlayer.playerID) + " (" + mPlayer.role.name + ") was lynched by an angry mob!")
    
    def AlivePlayers(self):
        return [mPlayer.playerID for mPlayer in mGame.players if mPlayer.isAlive]
    
    def AlivePlayersExcept(self, playerID):
        return [mPlayer.playerID for mPlayer in mGame.players if mPlayer.isAlive and not mPlayer.playerID == playerID]
    
    def AliveNonWerewolves(self):
        return [mPlayer.playerID for mPlayer in mGame.players if mPlayer.isAlive and not mPlayer.role == Role.Werewolf]
    
    def AliveWerewolves(self):
        return [mPlayer.playerID for mPlayer in mGame.players if mPlayer.isAlive and mPlayer.role == Role.Werewolf]

    def HaveWerewolvesWon(self):
        return len(self.AliveNonWerewolves()) <= len(self.AliveWerewolves())
    
    def HaveVillagersWon(self):
        return len(self.AliveWerewolves()) == 0

class AI(object):
    def __init__(self, playerID, role):
        self.playerID = playerID
        self.role = role
        self.isAlive = True
    
    def Doctor(self):
        # select a random living person to save, unless we're dead
        if not self.isAlive:
            return -1
        else:
            return random.choice(mGame.AlivePlayers())
    
    def Werewolf(self, chosen):
        # if we're trying to agree, randomly choose between the two options
        options = []
        for key, value in chosen.items():
            options.append(value)
        if len(options) > 0:
            return random.choice(options)
        
        # otherwise, select a random living non-werewolf person to kill, unless we're dead
        if not self.isAlive:
            return -1
        else:
            return random.choice(mGame.AliveNonWerewolves())
    
    def Seer(self):
        return random.choice(mGame.AlivePlayersExcept(self.playerID))
    
    def Discover(self, playerID, playerRole):
        pass
        
    def Villager(self):
        if self.role == Role.Werewolf:
            # werewolves will only vote for people who are not also werewolves
            return random.choice(mGame.AliveNonWerewolves())
        else:
            return random.choice(mGame.AlivePlayersExcept(self.playerID))
    
if __name__ == "__main__":
    mGamesToPlay = 10000
    mVictories = {"Villager" : 0, "Werewolf" : 0}
    for i in range(0, mGamesToPlay):
        mGame = Game(12)
        mVictories[mGame.Play()] += 1
    print(str(mVictories))