clear
close all
clc
%%
x=fileread('Caputo_Castellini.csv');

a=ismember(x, char([10 13]));
ind=find(a==1);

jj=0;
for ii=1:length(ind)-1
    r=x(ind(ii):ind(ii+1));
    if(rem(ii,2) == 0)
        jj=jj+1;
        riga{jj}=r;
    end
end

riga=riga';