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
            self.players.append(AI(i, Role.Villager, self.numPlayers))
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
            if mPlayer.role == Role.Doctor and mPlayer.isAlive:
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
        else:
            if self.Debug:
                print("The doctor managed to save Player #" + str(mPersonToSaveID) + "!")
            for mPlayer in self.players:
                if mPlayer.role == Role.Doctor:
                    mPlayer.DeclareSaved()

        # now determine whose role the Seer discovers
        for mPlayer in self.players:
            if mPlayer.role == Role.Seer and mPlayer.isAlive:
                mPlayerToDiscover = mPlayer.Seer()
                for mPlayer2 in self.players:
                    if mPlayer2.playerID == mPlayerToDiscover:
                        # The only information received is whether or not they're a werewolf
                        if(mPlayer2.role == Role.Werewolf):
                            mPlayer.Discover(mPlayerToDiscover, Role.Werewolf)
                        else:
                            mPlayer.Discover(mPlayerToDiscover, Role.Villager)

        # this is the end of the nighttime round

    def Day(self):
        votes = []
        for i in range(0, self.numPlayers):
            votes.append(0)

        isConsensus = False
        while not isConsensus:
            for mPlayer in self.players:
                if mPlayer.isAlive:
                    votes[mPlayer.Villager()] += 1

            # Check if we have a consensus
            mMax = 0
            for i in range(0, self.numPlayers):
                if votes[i] > mMax:
                    mMax = votes[i]
                    isConsensus = True
                elif votes[i] == mMax:
                    isConsensus = False
            if isConsensus:
                break
            else:
                # Report the results
                for mPlayer in self.players:
                    if mPlayer.isAlive:
                        mPlayer.VotingResults(votes)
                # Zero out the votes to try again
                for i in range(0, self.numPlayers):
                    votes[i] = 0

        # Now that we know we have a consensus, we have a unique max value and can kill them.
        playerToKill = votes.index(max(votes))
        for mPlayer in self.players:
            mPlayer.VotingDone(playerToKill)
            if mPlayer.playerID == playerToKill:
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

    def Accuse(self, fromPlayer, aboutPlayer, role):
        if(self.Debug):
            print("Player #" + str(fromPlayer) + " says that Player #" + str(aboutPlayer) + " is a " + role.name)
        for mPlayer in self.players:
            if mPlayer.isAlive:
                mPlayer.Accusation(fromPlayer, aboutPlayer, role)

class AI(object):
    def __init__(self, playerID, role, numPlayers):
        self.playerID = playerID
        self.role = role
        self.isAlive = True
        self.plannedMurder = -1

        # We keep track of our knowledge via a dictionary
        self.mThoughts = {}
        for mID in range(0, numPlayers):
            self.mThoughts[mID] = Role.Unknown

        # Even if we're a werewolf, we pretend to be a villager
        self.mThoughts[self.playerID] = Role.Villager

    def Accusation(self, fromPlayer, aboutPlayer, role):
        # If someone says we're a werewolf, protest!
        if aboutPlayer == self.playerID:
            if role == Role.Werewolf:
                mGame.Accuse(self.playerID, self.playerID, Role.Villager)
                if random.randint(1, 5) == 1:
                    # We might accuse them of being a werewolf in return!
                    self.mThoughts[fromPlayer] = Role.Werewolf
                    mGame.Accuse(self.playerID, fromPlayer, Role.Werewolf)
                return
        
        # Assume villagers are telling the truth
        if self.mThoughts[fromPlayer] == Role.Villager:
            self.mThoughts[aboutPlayer] = role
        else:
            # Assuming there's not a direct contradiction, there's a 20% chance of belief
            if self.mThoughts[aboutPlayer] == Role.Unknown:
                if random.randint(1, 5) == 1:
                    if mGame.Debug:
                        print("Player #" + str(self.playerID) + " believed Player #" + str(fromPlayer) + "'s statement that Player #" + str(aboutPlayer) + " is a " + role.name + "!")
                    self.mThoughts[aboutPlayer] = role

    def DeclareSaved(self):
        if self.role == Role.Doctor:
            self.mThoughts[self.saveChoice] = Role.Villager
            mGame.Accuse(self.playerID, self.saveChoice, Role.Villager)

    def Doctor(self):
        # select a random living person to save, unless we're dead
        if not self.isAlive:
            return -1
        else:
            self.saveChoice = random.choice(mGame.AlivePlayers())
            return self.saveChoice

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
        # discover players we don't know
        unknowns = []
        for mID in mGame.AlivePlayersExcept(self.playerID):
            if self.mThoughts[mID] == Role.Unknown:
                unknowns.append(mID)
        if len(unknowns) > 0:
            return random.choice(unknowns)
        else:
            return -1

    def Discover(self, playerID, playerRole):
        self.mThoughts[playerID] = playerRole
        mGame.Accuse(self.playerID, playerID, playerRole)

    def Villager(self):
        if self.role == Role.Werewolf:
            # werewolves will only vote for people who are not also werewolves
            return random.choice(mGame.AliveNonWerewolves())
        else:
            # if we've got a planned murder, carry it out.
            if not self.plannedMurder == -1:
                return self.plannedMurder

            # only vote for people who you don't know about
            mSuspects = []
            for mPID in mGame.AlivePlayersExcept(self.playerID):
                if self.mThoughts[mPID] == Role.Werewolf:
                    mSuspects.append(mPID)
            if len(mSuspects) > 0:
                return random.choice(mSuspects)
            else:
                for mPID in mGame.AlivePlayersExcept(self.playerID):
                    if self.mThoughts[mPID] == Role.Unknown:
                        mSuspects.append(mPID)
            if len(mSuspects) > 0:
                return random.choice(mSuspects)
            else:
                return random.choice(mGame.AlivePlayersExcept(self.playerID))

    def VotingResults(self, results):
        random.shuffle(results)
        self.plannedMurder = results.index(max(results))

    def VotingDone(self, lynchedID):
        self.plannedMurder = -1

if __name__ == "__main__":
    mGamesToPlay = 1000
    mVictories = {"Villager" : 0, "Werewolf" : 0}
    for i in range(0, mGamesToPlay):
        mGame = Game(12)
        # mGame.Debug = True
        mVictories[mGame.Play()] += 1
    print(str(mVictories))
