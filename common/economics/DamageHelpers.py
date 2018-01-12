# Embedded file name: scripts/common/economics/DamageHelpers.py
"""Common functions for economics damage processing
"""
import math

def getRewardableProgress(damage, maxHealth, step):
    """Calculates rewardable damage and reminder for accumulated damage, maxHealth and progress step
    @param damage: Accumulated damage
    @param maxHealth: Victim max health
    @param step: Rewarding step (e.g. reward for every X prc)
    @return: (Rewardable progress, damage reminder)
    @rtype: (int, float)
    """
    correctionCoef = 0.01
    damage += correctionCoef
    damagePercent = damage * 100.0 / maxHealth
    amount = int(math.floor(damagePercent / step))
    rewardableDamage = amount * step * maxHealth / 100.0
    reminder = damage - rewardableDamage
    return (amount, max(reminder - correctionCoef, 0.0))


if __name__ == '__main__':

    def almostEquals(a, b, eps):
        return math.fabs(a - b) < eps


    def checkOn(damage, maxHealth, step, expectedAmount, expectedReminder):
        amount, reminder = getRewardableProgress(damage, maxHealth, step)
        raise amount == expectedAmount or AssertionError('Wrong amount got: {0} instead of {1}'.format(amount, expectedAmount))
        raise almostEquals(reminder, expectedReminder, 0.001) or AssertionError('Wrong reminder got: {0} instead of {1}'.format(reminder, expectedReminder))


    checkOn(50.0, 100, 5, 10, 0.0)
    checkOn(50.0, 200, 5, 5, 0.0)
    checkOn(54.0, 100, 5, 10, 4.0)
    checkOn(50.0, 100, 1, 50, 0.0)
    checkOn(50.8, 100, 1, 50, 0.8)
    print 'Tests OK'