from gym.envs.registration import register

register(
         id='VacCan-v0',
         entry_point='Temp_Ctrl.envs:VacCan',
         )
register(
         id='VacCan-extrahard-v0',
         entry_point='Temp_Ctrl.envs:VacCanExtraHardEnv',
         )
