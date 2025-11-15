from flask import Flask,jsonify request

app=Flask(__name__

@app.route("/greet",methods=["GET","POST"]
def greet( 
    if request.method=="POST":
         name=request.json.get("name","World"
    else:
            name=request.args.get("name","World"
    message= "Hello, "+name+"!"
    return jsonify({"message":message,"length":len(message)})

@app.route("/broken"
def broken(
    value= request.args.get("value","default")
    if value == "explode":
          return jsonify({"status":"boom"}),500
    elif value=="warn":
      return jsonify({"status":"warn"}),400
    return jsonify({"status":"ok"})

if __name__=="__main__
 app.run(debug=True,port=5001

