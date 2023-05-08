var form = document.querySelector("#dform") || false,
  spinner = document.querySelector(".spinner");

function getCSRFToken() {
  const cookieValue = document.cookie.match(/csrftoken=([\w-]+)/);
  return cookieValue ? cookieValue[1] : null;
}

function validURL(str) {
  var pattern = new RegExp(
    "^(https?:\\/\\/)?" + // protocol
      "((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|" + // domain name
      "((\\d{1,3}\\.){3}\\d{1,3}))" + // OR ip (v4) address
      "(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*" + // port and path
      "(\\?[;&a-z\\d%_.~+=-]*)?" + // query string
      "(\\#[-a-z\\d_]*)?$",
    "i"
  ); // fragment locator
  return !!pattern.test(str);
}

form.onsubmit = function () {
  var scanFormContainer = document.querySelector("#tool2"),
    formE = this;

  var domainInputValue = this.elements[1].value,
    domainInput = this.elements[1],
    toolTip = document.createElement("span");

  toolTip.className = "tooltiptext";
  toolTip.innerHTML = "<span>!</span>Input a valid domain";

  if (domainInputValue == "" || !validURL(domainInputValue)) {
    domainInput.parentNode.appendChild(toolTip);
    setTimeout(function () {
      domainInput.parentNode.removeChild(toolTip);
      spinner.style.display = "none";
    }, 5000);
    return false;
  } else {
    domainInput.style.border = "";
  }
  spinner.style.display = "";

  // const isSubdomain = (domain) => domain.split('.').length > 3 && !/^(com|net|org|edu|gov)$/i.test(domain.split('.')[domain.split('.').length - 1]);
  // const tLD = domainInputValue.match(/[^.]*\.[^.]{2,5}(?:\.[^.]{2,5})?\/$/mg);

  var toolOverlay = new DOMParser().parseFromString(
      '<div class="tool-overlay backdrop-blur"><div class="inner"><h4></h4><p></p><button></button><button>Back</button></div></div>',
      "text/html"
    ),
    toolOverlayContainer = toolOverlay.querySelector("div");

  var startScan = (domain) => {
    const csrftoken = this.querySelector("[name=csrfmiddlewaretoken]").value;
    axios
      .post(
        "/portscan",
        {
          domain: domain,
        },
        {
          headers: {
            "X-CSRFTOKEN": csrftoken,
            contentType: "application/json",
          },
        }
      )
      .then(function (response) {
        domainInput.value = "";
        if (response.data.error) {
          if (response.data.message == "Invalid Domain") {
            toolTip.innerHTML = "<span>!</span>" + response.data.message;
            domainInput.parentNode.appendChild(toolTip);

            setTimeout(function () {
              domainInput.parentNode.removeChild(toolTip);
            }, 5000);

            spinner.style.display = "none";
            domainInput.value = response.data.domain;
          } else {
            toolOverlay.querySelectorAll("button")[0].style.display = "none";
          }
        } else {
          populateOverallOverview(domain);
        }
        console.log(response, "t-response");
      })
      .catch(function (error) {
        console.log(error, "error generated");
      });
    domainInput.value = "";
    return false;
  };

  // cancel button
  toolOverlay.querySelectorAll("button")[1].onclick = () => {
    scanFormContainer.removeChild(toolOverlayContainer);
    spinner.style.display = "none";
  };

  return startScan(domainInputValue);
};

function deletedomain(btn) {
  var scanFormContainer = document.querySelector("#tool2");

  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const headers = {
    "X-CSRFTOKEN": csrftoken,
    contentType: "application/json",
  };
  var dm = btn.id;

  var toolOverlay = new DOMParser().parseFromString(
      '<div class="tool-overlay backdrop-blur"><div class="inner"><h4></h4><p></p><button>Delete</button><button>Back</button></div></div>',
      "text/html"
    ),
    toolOverlayContainer = toolOverlay.querySelector("div");

  toolOverlay.querySelector("h4").innerHTML =
    'Delete domain "' + btn.getAttribute("data-domain") + '"?';
  toolOverlay.querySelector("p").innerHTML =
    "This scan will be deleted and removed from your account. You can always start a new scan of this domain.";
  // proceed deleting button
  toolOverlay.querySelectorAll("button")[0].onclick = () => {
    axios
      .post(
        "/api/deleteport",
        {
          domain: dm,
        },
        {
          headers: headers,
        }
      )
      .then(function (response) {
        console.log(response);
        populateOverallOverview();
      });
    scanFormContainer.removeChild(toolOverlayContainer);
  };
  // cancel button
  toolOverlay.querySelectorAll("button")[1].onclick = () => {
    scanFormContainer.removeChild(toolOverlayContainer);
  };
  scanFormContainer.appendChild(toolOverlay.querySelector("div"));
}

function populateOverallOverview(domain) {
  var axiosCall = (response) => {
    if ($("#firstTabOverall tr")) $("#firstTabOverall tr").remove();

    var table = document.getElementById("firstTabOverall");

    // helper function
    function addCell(tr, text) {
      var td = tr.insertCell();
      td.innerHTML = text;
      return td;
    }

    // create header
    var thead = table.createTBody();
    thead.id = "tablehead";
    // var headerRow = thead.insertRow();
    // headerRow.id = "headertab";
    // addCell(headerRow, 'Domain');
    // addCell(headerRow, 'Date');
    // addCell(headerRow, 'Time Start');
    // addCell(headerRow, 'Time End');
    // addCell(headerRow, 'Status');
    spinner.style.cssText = "display: none !important";

    // addCell(headerRow, 'Amount');
    var item = response.data.graph;
    console.log(item);
    // insert data
    item.forEach(function (result) {
      var row = table.insertRow(),
        timeStart =
          result.timeDateStart.match(/([0-9]{4}-[0-9]{2}-[0-9]{2})/gi)[0] +
          " " +
          result.timeDateStart.match(/([0-9]+(:[0-9]+)+)/gi)[0],
        timeEnd = result.timeDateEnd
          ? result.timeDateEnd.match(/([0-9]{4}-[0-9]{2}-[0-9]{2})/gi)[0] +
            " " +
            result.timeDateEnd.match(/([0-9]+(:[0-9]+)+)/gi)[0]
          : result.timeDateEnd;

      // row.id=result.description
      addCell(row, result.domain);
      // addCell(row, result.published);
      addCell(row, timeStart);

      // addCell(row, "delete")
      if (result.pending == 1) {
        addCell(row, timeEnd);
        // var result=result.time
        // var result1 = result.split('.')[0];
        row.removeAttribute("style");
        var btnCont = document.createElement("td"),
          button1 = document.createElement("BUTTON"),
          text1 = document.createTextNode("View Report");
        // btnCont.setAttribute('align', 'right');
        btnCont.setAttribute("style", "padding-right: 0;");
        button1.appendChild(text1);
        button1.id = result.domain;

        btnCont.appendChild(button1);
        row.appendChild(btnCont);
        button1.addEventListener("click", () => {
          viewgraph(button1);
        });
        /////////////////////////////////////////////
        var button = document.createElement("BUTTON");
        var text = document.createTextNode("Delete");

        button.appendChild(text);
        button.id = result.id;
        button.setAttribute("data-domain", result.domain);
        btnCont.appendChild(button);
        // row.appendChild(button);
        button.addEventListener("click", () => {
          deletedomain(button);
        });
        /////////////////////////////////////////////
      } else {
        row.style.backgroundColor = "#008b8b";
        addCell(row, "-");
        addCell(
          row,
          '<span style="margin-right: 5px;">Scanning</span><span class="spinner justify-content-center" style="position: unset; background-color: unset; padding-top: 0;"><span style="display: table-cell;" class="dot1 bg-light rounded-circle m-2"></span><span style="display: table-cell;" class="dot2 bg-light rounded-circle m-2"></span><span style="display: table-cell;" class="dot3 bg-light rounded-circle m-2"></span></span>'
        );
      }

      // Checking if array of domain is given
      if (typeof domain == "object") {
        for (var i = 0; i < domain.length; i++) {
          if (result.domain == domain[i] && result.pending == 1) {
            domain.splice(domain.indexOf(domain[i]), 1);
          }
        }
        if (domain.length == 0) clearInterval(checkDomainStatus);
      }
      // checking if single string of domain is given
      if (
        typeof domain != "object" &&
        result.domain == domain &&
        result.pending == 1
      ) {
        clearInterval(checkDomainStatus);
        // axios.post(
        //   "/api/generatenmapxmlreport",
        //   { domain: domain },
        //   {
        //     headers: {
        //       "X-CSRFToken": getCSRFToken(),
        //       "Content-Type": "application/json",
        //     },
        //   }
        // );
        console.log("cleared");
      }
    });
  };
  if (!domain) {
    return axios.get("/api/porttable").then(axiosCall);
  }
  var checkDomainStatus = setInterval(function () {
    axios.get("/api/porttable").then(axiosCall);
  }, 2000);
}

function viewgraph(btn) {
  var dm = btn.id;
  window.localStorage.setItem("graphname", dm);
  window.location.href = "/api/portinfo/" + dm + '/' + dm;
}
