import streamlit as st
from utils.yfinance_data import get_stock_data
from database.connection import connect
from utils.queries import get_strikes, get_expiries, get_underlyings
from pricing_engine.black import BlackScholes
from pricing_engine.binomial import BinomialTree, BinomialTreeVisual
from pricing_engine.monte import MonteCarloSimulation
from utils.visuals import plot_heatmap, plot_tree
import matplotlib.pyplot as plt


BINOMIAL_TREE = 'Binomial Tree'
BLACK_SCHOLES = 'Black Scholes Model'
MONTE_CARLO = 'Monte Carlo Simulation'

MODELS = (BLACK_SCHOLES, BINOMIAL_TREE, MONTE_CARLO)


#database connection and cache

@st.cache_resource
def wrap_db_connection():
    return connect()

engine = wrap_db_connection()

assets = sorted(get_underlyings(engine))

#inital asset formating
c = st.container()

heatmap_container = st.container()

c.title("Option Pricing Platform", text_alignment="center")

c.info("""Select an option pricing model to get started! From there, follow the input parameters
       to find theoretical fair values for live options in the market for an underlying
       that interests you!""")

#session state initialization

if "model" not in st.session_state:
    st.session_state.model = None
if "asset" not in st.session_state:
    st.session_state.asset = None
if "call" not in st.session_state:
    st.session_state.call, st.session_state.put = "Select Asset to Calculate", "Select Asset to Calculate"
if "und" not in st.session_state:
    st.session_state.und = 0.00
if 'iv' not in st.session_state:
     st.session_state.iv = 0.00
if 'strikes' not in st.session_state:
     st.session_state.strikes = None
if 'expiries' not in st.session_state:
     st.session_state.expiries = None
if 'expiry' not in st.session_state:
     st.session_state.expiry = None
if 'strike' not in st.session_state:
     st.session_state.strike = None
if 'asset_enabled' not in st.session_state:
     st.session_state.asset_enabled = True
if 'strike_enabled' not in st.session_state:
     st.session_state.strike_enabled = True
if 'expiry_enabled' not in st.session_state:
    st.session_state.expiry_enabled = True
if 'expiry_selected' not in st.session_state:
    st.session_state.expiry_selected = False
if 'N_disabled' not in st.session_state:
    st.session_state.N_disabled = True
if 'N' not in st.session_state:
    st.session_state.N = None
if 'sims' not in st.session_state:
     st.session_state.sims = None
if 'sim_disabled' not in st.session_state:
     st.session_state.sim_disabled = True


subheader = c.subheader(st.session_state.model)
call_placeholder = c.empty()


#custom html/css function for displaying call/put prices

def render_prices(call_price, put_price):
    call_placeholder.markdown(f"""
    <div style="display: flex; gap: 16px; width: 100%; margin: 12px 0;">
        <div style="
            flex: 1;
            background-color: #d4f4dd;
            border: 2px solid #2e7d32;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        ">
            <div style="font-size: 16px; color: #1b5e20; font-weight: 600;">CALL</div>
            <div style="font-size: 32px; color: #1b5e20; font-weight: 700;">${call_price}</div>
        </div>
        <div style="
            flex: 1;
            background-color: #fbdada;
            border: 2px solid #c62828;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        ">
            <div style="font-size: 16px; color: #8e0000; font-weight: 600;">PUT</div>
            <div style="font-size: 32px; color: #8e0000; font-weight: 700;">${put_price}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)



# black scholes state display
def display():

    call_option, put_option = compute_option()

    st.session_state.call = round(call_option.call(), 2)
    st.session_state.put  = round(put_option.put(), 2)

    render_heatmaps()
    
    compute_greeks(call_option, put_option)

    st.session_state.strike_enabled = True
    st.session_state.expiry_enabled = True


                                 
def set_model_state():
    st.session_state.asset_enabled = (st.session_state.model is None)


def set_asset_state():
    data = get_stock_data(st.session_state.asset)
    st.session_state.und = data[0]
    st.session_state.iv = data[1] * 100
    st.session_state.strikes = sorted(list(set(get_strikes(st.session_state.asset, 'call', engine))))
    st.session_state.strike = None       
    st.session_state.expiry = None
    st.session_state.expiries = None
    st.session_state.strike_enabled = False
    st.session_state.expiry_enabled = True  


def set_strike_state():

    st.session_state.expiries = sorted(get_expiries(st.session_state.asset, 'call', st.session_state.strike, engine))
    st.session_state.expiry_enabled = False


def compute_option():

    if st.session_state.model == BLACK_SCHOLES:

        call_option = BlackScholes(st.session_state.und,
                                         st.session_state.strike,
                                         .02,
                                         st.session_state.expiry,
                                         st.session_state.iv/100
                                         )
    
        put_option = BlackScholes(st.session_state.und,
                                        st.session_state.strike,
                                        .02,
                                        st.session_state.expiry,
                                        st.session_state.iv/100
                                        ,False)
        return call_option, put_option
    

    elif st.session_state.model == BINOMIAL_TREE:

        call_option = BinomialTree(st.session_state.und,
                                        st.session_state.strike,
                                        st.session_state.expiry,
                                        .02,
                                        st.session_state.iv/100,
                                        int(st.session_state.N))
        put_option = BinomialTree(st.session_state.und,
                                        st.session_state.strike,
                                        st.session_state.expiry,
                                        .02,
                                        st.session_state.iv/100,
                                        int(st.session_state.N))
        return call_option, put_option
    
    elif st.session_state.model == MONTE_CARLO:
        sim = MonteCarloSimulation(st.session_state.und,
                                   st.session_state.strike,
                                   st.session_state.expiry,
                                    .02,
                                    st.session_state.iv/100,
                                    int(st.session_state.sims)
                                    )
        
        return sim

def render_heatmaps():

    c_fig, c_ax = plt.subplots()
    p_fig, p_ax = plt.subplots()

    plot_heatmap(st.session_state.und, 
                            st.session_state.strike, 
                            .02, st.session_state.expiry, 
                            st.session_state.iv, 
                            c_ax, 
                            p_ax)
    
    heatmap_container.header("Heatmaps", text_alignment='center')
    heatmap_container.info("""Explore how options price fluctuates with varying 'Spot Price
                           and Volatility' levels with call and put heatmap visualizations""")
    
    call, put = heatmap_container.columns(2)
   
    call.subheader("Call Heatmap")
  

    call.pyplot(c_fig)

    put.subheader("Put Heatmap")
    put.pyplot(p_fig)


def compute_greeks(call_option, put_option): 

    call, put = heatmap_container.columns(2)

    call.slider('Call Delta', min_value=0.0, max_value= 100.00, value=call_option.delta() * 100)
    call.slider('Call Gamma', min_value=0.0, max_value= 1.0, value=call_option.gamma())
    call.slider('Call Theta', max_value= 0.0, min_value=-100.0, value=call_option.theta())
    call.slider('Vega', min_value=0.0, max_value= 100.0, value=call_option.vega())
    call.slider('Call Rho', min_value=0.0, max_value= 1.0, value=call_option.rho())

    put.slider("Put Delta", min_value=-100.00, max_value= 0.0, value=put_option.delta() * 100)
    put.slider("Put Gamma", min_value = 0.0, max_value= 1.0, value =put_option.gamma())
    put.slider('Put Theta', min_value= -100.0, max_value= 0.0, value=put_option.theta())
    put.slider('Vega', min_value=0.0, max_value= 100.00, value=put_option.vega())
    put.slider('Put Rho', min_value=-1.0, max_value= 0.0, value=put_option.rho())

def set_expiry_state():
    st.session_state.expiry_selected = True

    if st.session_state.model == BINOMIAL_TREE:
        st.session_state.N_disabled = False

    if st.session_state.model == MONTE_CARLO:
         st.session_state.sim_disabled = False


# main rendering script based on model state

if st.session_state.model == BLACK_SCHOLES:

    c.latex("C_{Call} = S_0N(d_1) - K * e^{-rT} N(d_2)")
    c.latex("P_{Put} = Ke^{-rT}N(-d_2) - S_0N(-d_1)")
    c.latex("d_1 = \\frac{ln{(S_0/K)} + {(r + \sigma^2 / 2)}T}{\sigma \sqrt{T}}")
    c.latex("d_2 = d_1 - \sigma\sqrt{T}")

    c.subheader("The Greeks", help="""
                                Learn about the key risk metrics in options trading, The Greeks. 
                                Used by traders to hedge positions, create spreads, and mitgate risk.
                                You can learn more about each of the Greeks below or visit here: """)
    
    c.latex(f"\Delta \ Delta", width='content', help="""In option theory, Delta represents 
                                                        an options sensitivity to a change 
                                                        in the underlying assets price.
                                                    """)
    
    c.latex("\Gamma \ Gamma ", width='content', help="""
                                                    Gamma measures how much an option's Delta changes when 
                                                    the underlying asset price moves by $1.00.
                                                    """)
    c.latex("\Theta \  Theta", width='content', help="""
                                                    Theta, or time decay, measures 
                                                    the rate at which an option's price declines 
                                                    as time passes
                                                    """)
    c.latex("v \ Vega", width='content', help="""
                                                Vega measures how much an option's price changes 
                                                when implied volatility moves by 1%. It is easy to 
                                                remember Vey-Ga, Vol-Atiliy.
                                                """)
    c.latex("\\rho \ Rho", width='content', help="""
                                                Rho (the least important greek) measures
                                                how much an option's price changes when the risk-free 
                                                interest rate changes by 1%""") 

    if st.session_state.expiry and st.session_state.strike:
        display()
        render_prices(st.session_state.call, st.session_state.put)

elif st.session_state.model == BINOMIAL_TREE:
        
        if st.session_state.N and st.session_state.N <= 0:
            st.session_state.N = 500

        if st.session_state.N and st.session_state.N > 0:
                call_option, put_option = compute_option()
                st.session_state.call = round(call_option.calculate_call(), 2)
                st.session_state.put  = round(put_option.calculate_put(), 2)
                render_prices(st.session_state.call, st.session_state.put)
                tree_to_vis = BinomialTreeVisual(call_option)
                premium = tree_to_vis.build_tree()
                fig = plot_tree(tree_to_vis.stock_tree, tree_to_vis.value_tree, tree_to_vis.N)
                st.plotly_chart(fig, use_container_width=True)
else:

        if st.session_state.sims and st.session_state.sims <= 0:
             st.session_state.sims = 500
        
        if st.session_state.sims and st.session_state.sims > 0:
             
             #construct the simulation object
             sim = compute_option()

             #simulate prices
             sim.simulate_prices()

             st.session_state.call = round(sim._calculate_call_option_price())
             st.session_state.put = round(sim._calculate_put_option_price())
             render_prices(st.session_state.call, st.session_state.put)
             res = sim.plot_simulation_results(500)
             st.pyplot(res)

#sidebar data/inputs

model_select_box = st.sidebar.selectbox(
    'Option Model', 
    MODELS,
    key='model',
    on_change=set_model_state,
    placeholder='Select Pricing Model'
    )

asset_select_box = st.sidebar.selectbox(
    'Underlying Asset',
    assets,
    key='asset',
    on_change=set_asset_state,
    placeholder='Select Underlying',
    disabled=st.session_state.asset_enabled

)   

und_price = st.sidebar.text_input("Underlying Price" , f"${round(st.session_state.und, 2)}", disabled=True)


strike_prices = st.sidebar.selectbox("Strike Prices",
                                     st.session_state.strikes, 
                                     key = 'strike',
                                     placeholder='Select Strike Price',
                                     on_change=set_strike_state,
                                     disabled=st.session_state.strike_enabled)


expirations = st.sidebar.selectbox("Time-Till-Expiration",
                                   st.session_state.expiries,
                                   key = 'expiry',
                                   placeholder='Select an Expiration Date',
                                   on_change=set_expiry_state,
                                   disabled=st.session_state.expiry_enabled,
                                   )


iv = st.sidebar.text_input("Implied Volatility" , f"{round(st.session_state.iv, 2)}%", disabled= True, placeholder='Implied Volatility')

if st.session_state.model == BINOMIAL_TREE:

    steps_select_box = st.sidebar.number_input("Number of Steps (N)",
                                             key = 'N',
                                             help="""Input the number of steps into 
                                             the future you wish to simulate. Note: The
                                             greater the number the more accurate the theoretical
                                             price, though the longer the calculation will take.
                                             Recommended N between 500 - 10000""",
                                             disabled=st.session_state.N_disabled,
                                             )

if st.session_state.model == MONTE_CARLO:

    simulation_select_box = st.sidebar.number_input(
                                        "Number of Simulations to Run",
                                        key='sims',
                                        disabled=st.session_state.sim_disabled,
                                        )