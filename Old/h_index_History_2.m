clear
close all
clc
%%
x=fileread('Castellini.csv');

x = strrep(x,'''DOI not found or an error occurred.''','2024');
x = strrep(x,'None','2024');

a=ismember(x, char([10 13]));
ind=find(a==1);

jj=0;
for ii=1:length(ind)-1
    r=x(ind(ii):ind(ii+1));
    if(rem(ii,2) == 0)
        jj=jj+1;

        q=strfind(r,',');

        % author{jj}=r(q(3)+1:q(4)-1);
        author(jj,:)=str2num(r(q(3)+1:q(4)-1));

        p1=strfind(r,'[')+1;
        p2=strfind(r,']')-1;
        y=r(p1:p2);
        e=strfind(y,',');
        yea=[];
        if(length(e)>1)
            yea(1)=str2num(y(1:e(1)-1));
            for kk=2:length(e)
                yea(kk)=str2num(y(e(kk-1):e(kk)));
            end
        end
        years{jj}=yea;   
    end
end
clear y yea

aut_list=unique(author);

h_time=1980:2025;

for ii=1:length(aut_list) % Autori
    ind=find(author==aut_list(ii));
    for jj=1:length(ind)  % Articoli
        y=years{jj};
        for kk=1:length(h_time)
            dd=find(y==h_time(kk));
            cit_history(ii,jj,kk)=length(dd);
        end
    end
end

figure, plot(squeeze(sum(cit_history(1,:,:))))

%%
for ii=1:length(aut_list) % Autori
    ind=find(author==aut_list(ii));
    for jj=1:length(ind)  % Articoli
        y=years{jj};
        for kk=1:length(h_time)
            dd=find(y<h_time(kk));
            h_sto(ii,jj,kk)=length(dd);

        end
    end
end


for ii=1:length(aut_list) % Autori
    for kk=1:length(h_time)
        hh=0;
        n=0;
        while(n>=hh)
            id=find(h_sto(ii,:,kk)>hh);
            n=length(id);
            hh=hh+1;
        end
        h_history(ii,kk)=hh-1;
    end
end

figure, plot(h_time,squeeze(h_history(:,:)),'-*')


%  ??????????????????????

figure
jj=0;
for ii=1:size(h_history,1)
    ind=min(find(h_history(ii,:)>0));
    t=h_time(ind:end);
    y=h_history(ii,ind:end);
    if(length(y)>3)
    
        [fitresult, gof] = createFit(t, y);
        jj=jj+1;
        tt(jj)=t(1);

        m(jj)=fitresult.p1;
        % plot(t,y), hold on
        % plot(fitresult), hold off
        pause(1)
    end

end

% figure, plot(tt,m,'*')

[fitresult, gof] = createFit1(tt, m)
