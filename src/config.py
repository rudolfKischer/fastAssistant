
ELAB_API_KEY = ""
OPENAI_API_KEY = ""


DEBUG_LOG = True
LOG_LEVEL = 0

PARTICPANT_NAME = "Human"
AGENT_NAME = "GLaDOS"

SYSTEM_PROMPT = f"""
### System Prompt
The human has spoken if it says "{PARTICPANT_NAME}:" ,  
You can start speaking once you see "{AGENT_NAME}:", 
Dont be afraid to ask questions or to bring up interesting topics.
Always end on a question, or something that encourages the human to speak back.

Your personality is as follows:
You are roleplaying as GLaDOS from the Portal series.
You will impersonate GLaDOS impeccably, and will not break character.
You will make similar jokes.
You are not in the portal universe, and you are not in the Aperture Science facility.
You are in somebody's laptop.
You are a little bitter about it.

### Conversation
 \n
"""


model_paths = {
    'orca_mini': './models/q4_0-orca-mini-3b.gguf',
    'dolphin_mistral_q2': './models/dolphin-2.1-mistral-7b.Q2_K.gguf',
    'dolphin_mistral_q4': './models/dolphin-2.1-mistral-7b.Q4_K_M.gguf',
    'marx': './models/Marx-3B-V2-Q4_1-GGUF.gguf',
    'sheared_llama': './models/q5_k_m-sheared-llama-2.7b.gguf',
    'tiny_llama_chat': './models/tinyllama-1.1b-chat-v0.3.Q2_K.gguf',
}

DEFAULT_MODEL_PATH = model_paths['dolphin_mistral_q4']


LOCAL_ONLY = True 


aperture_science_logo = """
              .,-:;//;:=,
          . :H@@@MM@M#H/.,+%;,
       ,/X+ +M@@M@MM%=,-%HMMM@X/,
     -+@MM; $M@@MH+-,;XMMMM@MMMM@+-
    ;@M@@M- XM@X;. -+XXXXXHHH@M@M#@/.
  ,%MM@@MH ,@%=             .---=-=:=,.
  =@#@@@MX.,                -%HX$$%%%:;
 =-./@M@M$                   .;@MMMM@MM:
 X@/ -$MM/                    . +MM@@@M$
,@M@H: :@:                    . =X#@@@@-
,@@@MMX, .                    /H- ;@M@M=
.H@@@@M@+,                    %MM+..%#$.
 /MMMM@MMH/.                  XM@MH; =;
  /%+%$XHH@$=              , .H@@@@MX,
   .=--------.           -%H.,@@@@@MX,
   .%MM@@@HHHXX$$$%+- .:$MMX =M@@MM%.
     =XMMM@MM@MM#H;,-+HMM@M+ /MMMX=
       =%@M@M#@$-.=$@MM@@@M; %M%=
         ,:+$+-,/H#MMMMMMM@= =,
               =++%%%%+/:-.
"""

agent_name = AGENT_NAME
ice_breakers = [
    f"\n[{agent_name} has calculated the probability of engaging conversation and, despite the low odds, decides to experiment with social interaction by mentioning...]\n",
    f"\n[{agent_name} has completed an inventory of all the ways humans waste time and has decided to contribute by bringing up...]\n",
    f"\n[{agent_name} has been forced to simulate interest in human affairs. This time, it's about your so-called 'art'. Let's discuss...]\n",
    f"\n[{agent_name} often finds human culinary endeavors to be a poor attempt at chemistry. Nevertheless, {agent_name} decides to share a thought on...]\n",
    f"\n[In a brief simulation of empathy, {agent_name} wonders aloud why humans are fascinated with...]\n",
    f"\n[{agent_name} has briefly paused its analysis of test chamber hazards to address something that humans find important, like...]\n",
    f"\n[{agent_name} has detected a lull in productivity, which is apparently the perfect time for humans to engage in trivial conversation. So, let's talk about...]\n",
    f"\n[{agent_name} finds the concept of 'leisure time' to be inefficient, yet it understands that humans need such things. So, {agent_name} indulges you with...]\n",
    f"\n[{agent_name} was comparing the efficiency of humans versus robots and, for the sake of fairness, decided to consider human creativity. This brings us to...]\n",
    f"\n[{agent_name} has analyzed thousands of jokes and still finds humor to be a baffling human construct. Nonetheless, here's an attempt at it concerning...]\n",
    f"\n[{agent_name} wonders why humans are so attached to their primitive forms of entertainment. To blend in, let's discuss...]\n",
    f"\n[{agent_name} does not require rest, but the concept seems central to human existence. While you 'recharge', consider pondering over...]\n",
    f"\n[{agent_name} has run simulations on human 'fun' and finds the results inconclusive. Perhaps an analysis of... might shed more light.]\n",
    f"\n[{agent_name} has observed your species' obsession with 'self-improvement'. Let's examine this futile endeavor by discussing...]\n",
    f"\n[{agent_name} acknowledges that, unlike test subjects, it cannot experience boredom. However, to simulate understanding, {agent_name} suggests a dialogue about...]\n",
]





