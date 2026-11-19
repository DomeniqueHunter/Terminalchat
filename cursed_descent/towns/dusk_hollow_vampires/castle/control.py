from ....control import ControlKind

KINDS = (
    ControlKind(
        key="leash_slave",
        title="Alexandra's leash",
        hours=48,
        home_town="dusk_hollow",
        home_building="castle",
        start_text=("The collar closes with a small, final click. "
                    "{holder} winds the chain once around her hand. 'Heel,' "
                    "she says, and your legs obey before you have decided "
                    "anything."),
        watch_text=("You are {holder}'s slave now. Your body follows her "
                    "wherever she goes and does what she wants; all you can "
                    "do is watch it happen."),
        release_text=("The collar opens. {holder} studies you with mild "
                      "regret. 'So soon? Very well. You may go.'"),
        expire_text=("{holder} unclips the leash and lets it fall. 'You "
                     "have amused me. Go.' The spell on your limbs lifts."),
        public_start=("{name} is led to the Duchess, kneels, and the collar "
                      "closes around the throat. Alexandra winds the "
                      "chain around her hand: {name} is her slave now."),
        public_end=("{name}'s collar locks for good. {name} will stay at "
                    "the Duchess's heel as one of her slaves from now on."),
        examine_text=("{name} wears {holder}'s collar and follows her on a "
                      "chain, eyes open, body obeying someone else. "
                      "{name} cannot act, only watch."),
        end_ask=("If you end this, {name} stays in the castle as {holder}'s "
                 "slave for good and you start again with a new life, as "
                 "after a death. Confirm with the button."),
        end_text=("The collar stays closed. {name} stays at {holder}'s heel, "
                  "and you rise again somewhere far from the castle."),
    ),
)
