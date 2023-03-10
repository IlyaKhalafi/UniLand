from pyrogram import Client, filters
import pyrogram
from uniland.utils.triggers import Triggers
import uniland.db.user_methods as user_db
from uniland.utils.steps import UserSteps
from uniland.utils.uxhandler import UXTree
from uniland.utils.filters import user_step, exact_match


@Client.on_message(
    filters.text
    & exact_match(Triggers.CHOOSE_SUBMISSION_TYPE.value)
    & user_step(UserSteps.START.value)
)
async def submission_type(client, message):
    # Asks user to choose submission type
    user_step = UXTree.nodes[UserSteps.CHOOSE_SUBMISSION_TYPE.value]
    await message.reply(text=user_step.description, reply_markup=user_step.keyboard)
    user_db.update_user_step(message.from_user.id, user_step.step)
