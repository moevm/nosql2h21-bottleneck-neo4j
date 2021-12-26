function CreateRequest()
{
    var Request = false;

    if (window.XMLHttpRequest)
    {
        Request = new XMLHttpRequest();
    }
    else if (window.ActiveXObject)
    {
        try
        {
            Request = new ActiveXObject("Microsoft.XMLHTTP");
        }
        catch (CatchException)
        {
            Request = new ActiveXObject("Msxml2.XMLHTTP");
        }
    }

    if (!Request)
    {
        alert("Невозможно создать XMLHttpRequest");
    }

    return Request;
}

function SendRequest(r_method, r_path, r_args, r_handler)
{
    var Request = CreateRequest();

    if (!Request)
    {
        return;
    }

    Request.onreadystatechange = function()
    {
        if (Request.readyState == 4)
        {
            if (Request.status == 200)
            {
                console.log("Response received, control transferred to ", r_handler);
                r_handler(Request);
            }
            else
            {
                console.log("Error:", Request.status);
                alert("Error! Error code:", Request.status)
            }
        }
        else
        {
            console.log("Awaiting response from ", r_path);
        }

    }

    if (r_method.toLowerCase() == "get" && r_args.length > 0)
        r_path += "?" + r_args;
    Request.open(r_method, r_path, true);

    if (r_method.toLowerCase() == "post")
    {
        Request.setRequestHeader("Content-Type","json; charset=utf-8");
        Request.send(r_args);
    }
    else
    {
        Request.send(null);
    }
}