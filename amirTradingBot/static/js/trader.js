
// ################################### Start engine ####################################
// #####################################################################################
document.getElementById("start").onclick = function() {

    var testSleep;
    const symbol = document.querySelector("#symbol").value;
    const engine = document.querySelector("#engine").value;
    const TP = document.querySelector("#TP").value;
    const SL = document.querySelector("#SL").value;
    const verticalOffset = document.querySelector("#verticalOffset").value;
    const timeFrame = document.querySelector("#timeFrame").value;
    const leverage = document.querySelector("#leverage").value;
    const amount = document.querySelector("#amount").value;

    if(this.textContent === "Start The Engine") {

        var engineStarted = 'true'
        fetch('/trader/engine-setup', {
            body: JSON.stringify({EngineStarted: engineStarted,
                                        symbol:symbol, engine:engine, TP:TP, SL:SL,
                                        verticalOffset:verticalOffset, timeFrame:timeFrame,
                                        leverage:leverage, amount:amount}),
            method: "POST"
        }).then(
            fetch('/trader/start-engine', {
                            body: JSON.stringify({}),
                            method: "POST"
            })
        )
        this.textContent = 'Stop The Engine'
        this.style.background='#fa0000';

    }else{

        var engineStarted = 'false'
        fetch('/trader/engine-setup', {
            body: JSON.stringify({EngineStarted: engineStarted,
                                        symbol:symbol, engine:engine, TP:TP, SL:SL,
                                        verticalOffset:verticalOffset, timeFrame:timeFrame,
                                        leverage:leverage, amount:amount}),
            method: "POST"
        })
        this.textContent = "Start The Engine"
        this.style.background='#2f9ce0';
    }
    }

