clear
close all
clc
%%
x=fileread('Castellini_eid_doi.csv');

x = strrep(x,'''DOI not found or an error occurred.''','0');
x = strrep(x,'None','0');

a=ismember(x, '[');
ini=find(a==1);

a=ismember(x, ']');
fini=find(a==1);

for ii=1:length(ini)
    s=x(ini(ii)+1:fini(ii)-1);
    if(length(s)>1)
        a=ismember(s, char([10 13]));
        ind=find(a==1);
        for jj=1:length(ind)-1
            r=s(ind(ii):ind(ii+1));
        end



end

