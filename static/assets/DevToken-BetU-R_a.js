import{_ as a,f as r,a as t,t as d,i as u,g as c,o as i}from"./index-PzTaAiWw.js";const k={name:"DevToken",data(){return{token:null,userId:null,loading:!1,error:null,copied:!1}},methods:{async getToken(){this.loading=!0,this.token=null,this.error=null,this.copied=!1;try{const n=await fetch("/api/auth/dev-token/",{method:"GET",headers:{Accept:"application/json"}});if(!n.ok)throw new Error(`Server responded with status: ${n.status}`);const e=await n.json();this.token=e.access_token,this.userId=e.user_id}catch(n){console.error("Error getting dev token:",n),this.error=`Failed to get development token: ${n.message}`}finally{this.loading=!1}},copyToken(){this.$refs.tokenInput.select(),document.execCommand("copy"),this.copied=!0,setTimeout(()=>{this.copied=!1},3e3)},saveAndRedirect(){this.token&&(localStorage.setItem("access_token",this.token),console.log("Development token saved to localStorage"),this.$router.push("/"))}}},p={class:"container my-4"},v={class:"card"},m={class:"card-body"},g={key:0,class:"text-center"},b={key:1,class:"alert alert-danger"},y={key:2},f={class:"alert alert-success"},T={class:"mb-3"},h={class:"input-group"},I=["value"],D={key:0,class:"text-success mt-1"},_={class:"mt-4"},C={key:3};function w(n,e,x,A,l,o){return i(),r("div",p,[t("div",v,[e[13]||(e[13]=t("div",{class:"card-header"},[t("h2",null,"Developer Token")],-1)),t("div",m,[l.loading?(i(),r("div",g,e[5]||(e[5]=[t("div",{class:"spinner-border",role:"status"},null,-1),t("p",null,"Loading...",-1)]))):l.error?(i(),r("div",b,[e[6]||(e[6]=t("h4",null,"Error",-1)),t("p",null,d(l.error),1),t("button",{class:"btn btn-primary mt-2",onClick:e[0]||(e[0]=(...s)=>o.getToken&&o.getToken(...s))},"Try Again")])):l.token?(i(),r("div",y,[t("div",f,[e[7]||(e[7]=t("p",null,[t("strong",null,"Development token generated successfully!")],-1)),t("p",null,"User ID: "+d(l.userId),1)]),t("div",T,[e[10]||(e[10]=t("label",{class:"form-label"},"Access Token:",-1)),t("div",h,[t("input",{type:"text",class:"form-control",value:l.token,readonly:"",ref:"tokenInput"},null,8,I),t("button",{class:"btn btn-outline-secondary",onClick:e[1]||(e[1]=(...s)=>o.copyToken&&o.copyToken(...s))},e[8]||(e[8]=[t("i",{class:"bi bi-clipboard me-1"},null,-1),c(" Copy ")]))]),l.copied?(i(),r("div",D,e[9]||(e[9]=[t("small",null,"Token copied to clipboard!",-1)]))):u("",!0)]),t("div",_,[t("button",{class:"btn btn-primary me-2",onClick:e[2]||(e[2]=(...s)=>o.saveAndRedirect&&o.saveAndRedirect(...s))}," Save Token & Go to Dashboard "),t("button",{class:"btn btn-outline-secondary",onClick:e[3]||(e[3]=(...s)=>o.getToken&&o.getToken(...s))}," Generate New Token ")]),e[11]||(e[11]=t("div",{class:"alert alert-warning mt-4"},[t("h5",null,"Developer Use Only"),t("p",null,"This token is for development and testing purposes only. It should not be used in production.")],-1))])):(i(),r("div",C,[e[12]||(e[12]=t("p",null,"Click the button below to generate a development token for testing the API:",-1)),t("button",{class:"btn btn-primary",onClick:e[4]||(e[4]=(...s)=>o.getToken&&o.getToken(...s))}," Generate Dev Token ")]))])])])}const S=a(k,[["render",w]]);export{S as default};
