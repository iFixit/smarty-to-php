<li><a rel="Answers" {if !($static->call('ServerConstants', 'enabled', 'feature-answers-is-discussion') 
 && $question->is_discussion) && !$showDeleted}class="active"{/if}>
<li><a rel="Oldest" {if $static->call('ServerConstants', 'enabled', 'feature-answers-is-discussion') && 
 $question->is_discussion && !$showDeleted}class="active"{/if}>

{if $question->status != 'closed'}{/if}

{if (!$isLoggedIn || $events->allowed('posts', 'new_answer')) && $question->status != 'closed'}
   {assign var='canAnswer' value=true}
{else}
   {assign var='canAnswer' value=false}
{/if}

{if (empty($sPaymentOption) and $smarty.foreach.paymentOptions.index == 0)
  or (!empty($sPaymentOption) and $sPaymentOption eq $payment.paymentid) 
  or (count($paymentTypes) == 1)}
   checked="checked"
{/if}

{if $modVoteAllowed|default:false && ($curUserid != $post->userid || $canForceVote|default:false)}{/if}
{if $aConf->search !== false} for <em>{$aConf->search|wordbreak:20}</em>{/if}
{if $question->userid === $curUserid &&
 (!$post->isQuestion) && !($question->is_discussion &&
 $static->call('ServerConstants', 'getSetting', 'feature-answers-is-discussion'))}
   &bull;
   <a id="acceptAnswer-{$post->postid}" class="muted toggleAcceptLink" 
   data-postid="{$post->postid}">
    {if $accepted}{t}Unaccept Answer{/t}{else}{t}Accept Answer{/t}{/if}</a>
{elseif $search}
   {t}Hello world{/t}
{/if}

 {if $question->blurb->is_discussion && $static->call('ServerConstants',
 'enabled', 'feature-answers-is-discussion')}{/if}

